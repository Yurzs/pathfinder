from struct import Struct

from pathfinder.common.dns.exceptions import DnsException

from pathfinder.common.dns.parts import DnsMessagePart


class DnsMessageHeader(DnsMessagePart):
    """Dns message header."""

    lengths = {
        # Length in binary format
        "id":      16,
        "qr":      1,
        "opcode":  4,
        "aa":      1,
        "tc":      1,
        "rd":      1,
        "ra":      1,
        "z":       3,
        "rcode":   4,
        "qdcount": 16,
        "ancount": 16,
        "nscount": 16,
        "arcount": 16
    }

    byte_length = int(sum(lengths.values()) / 8)

    structure = Struct("!{0}".format("".join({
        "id":      "H",
        "options": "H",
        "qdcount": "H",
        "ancount": "H",
        "nscount": "H",
        "arcount": "H"
    }.values())))

    def __init__(self, message, id=None, qr=None, opcode=None, aa=None, tc=None, rd=None,
                 ra=None, z=None, rcode=None, qdcount=None, ancount=None, nscount=None,
                 arcount=None):
        self._message = message
        self.id = id
        self.qr = qr
        self.opcode = opcode
        self.aa = aa
        self.tc = tc
        self.rd = rd
        self.ra = ra
        self.z = z
        self.rcode = rcode
        self._qdcount = qdcount
        self._ancount = ancount
        self._nscount = nscount
        self._arcount = arcount

    @property
    def qdcount(self):
        return len(self._message.question)

    @property
    def ancount(self):
        return len(self._message.answer)

    @property
    def nscount(self):
        return len(self._message.authority)

    @property
    def arcount(self):
        return len(self._message.additional)

    @property
    def options(self):
        """Proxy for 3rd and 4th octets with less than 1 byte fields."""

        result = ""
        order = ("qr", "opcode", "aa", "tc", "rd", "ra", "z", "rcode")
        for field in order:
            result += bin(getattr(self, field))[2:].zfill(self.lengths[field])
        return int(result, 2)

    @classmethod
    def unpack(cls, message, data: bytes):
        """Unpacks header from bytes."""

        header = cls(message)
        header.id, options, header._qdcount, header._ancount, header._nscount, header._arcount = \
            header.structure.unpack(data[:12])
        bin_options = bin(options)[2:].zfill(16)
        header.qr = bool(bin_options[0])
        header.opcode = int(bin_options[1:5], 2)
        header.aa = bool(int(bin_options[5]))
        header.tc = bool(int(bin_options[6]))
        header.rd = bool(int(bin_options[7]))
        header.ra = bool(int(bin_options[8]))
        header.z = int(bin_options[9:12], 2)
        header.rcode = int(bin_options[12:16], 2)
        return header

    def pack(self):
        """Packs header to bytes."""

        packed = self.structure.pack(
            self.id, self.options, self.qdcount, self.ancount, self.nscount, self.arcount
        )
        if len(packed) != self.byte_length:
            raise DnsException(f"Bad header length {len(packed)}")
        self._message.bytestream.write(packed)
        return packed
