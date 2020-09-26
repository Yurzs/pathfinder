import struct
import typing


class DomainStorage(list):
    def find_by_pos(self, pos: int) -> typing.Union["DnsDomain", None]:
        """Finds domain in storage by its position.

        :param pos: starting octet of domain
        :return: DnsDomain or None
        """

        for domain in self:
            if domain.pos == pos:
                return domain

    def find_by_label(self, label: str) -> typing.Union["DnsDomain", None]:
        """Finds domain in storage by its label.

        :param label: domain name
        :return: DnsDomain or None
        """

        for domain in self:
            if domain.label == label:
                return domain


class DnsDomain:
    def __init__(self, message, label="", position=None, can_be_shortened=True):
        self.message = message
        self.label = label
        self.pos = position
        self.shortable = can_be_shortened

    @property
    def byte_length(self) -> int:
        return len(self.pack())

    @classmethod
    def unpack(cls, message: "DnsMessage", data: "ByteStream") -> "DnsDomain":
        """Unpacks bytes to domain name."""

        domain = cls(message)
        pos = data.pos
        domain_length = struct.unpack("!B", data.peek(1))[0]
        while domain_length != 0:
            if domain_length >= 192:
                domain.label = f"{domain.label}." if domain.label else domain.label
                domain.label += domain.from_pos(struct.unpack("!H", data.read(2))[0] - 49152)
                break
            else:
                data.read(1)  # domain_length byte
                domain.label += data.read(domain_length).decode("ascii")
            domain_length = struct.unpack("!B", data.peek(1))[0]
            if 0 < domain_length < 192:
                domain.label += "."
        else:
            data.read(1)
        for n, subdomain in enumerate(domain.label.split(".")):
            dmn = ".".join(domain.label.split(".")[n:])
            message.domains.append(DnsDomain(message, dmn, pos))
            pos += len(subdomain) + 1
        return domain

    def from_pos(self, pos) -> str:
        """Finds domain by its start position octet."""

        return self.message.domains.find_by_pos(pos).label

    def pack(self) -> bytes:
        """Encodes domain to bytes."""

        packed = b""
        bs = self.message.bytestream
        md = self.message.domains

        for n, subdomain in enumerate(self.label.split(".")):
            if subdomain == "":
                break
            find_domain = ".".join(self.label.split(".")[n:])

            if self.message.domains.find_by_label(find_domain) and self.shortable:
                data = struct.pack("!H", md.find_by_label(find_domain).pos + 49152)
                md.append(DnsDomain(self.message, find_domain, self.message.bytestream.pos))
                bs.write(data)
                return packed + data

            md.append(DnsDomain(self.message, find_domain, self.message.bytestream.pos))
            data = struct.pack("!B", len(subdomain))
            data += subdomain.encode("ascii")
            packed += data
            bs.write(data)

        packed += struct.pack("!B", 0)
        bs.write(struct.pack("!B", 0))
        return packed

    def __repr__(self):
        return self.label

    def __eq__(self, other):
        if isinstance(other, DnsDomain):
            return other.label == self.label
        return other == self.label

    def lower(self):
        return self.label.lower()

    def upper(self):
        return self.label.upper()

    def split(self, sep=" ", maxsplit=-1):
        return self.label.split(sep=sep, maxsplit=maxsplit)
