import struct
import typing

from pathfinder.common.dns.parts import DnsMessagePart, rdata
from pathfinder.common.dns.domains import DnsDomain


class DnsMessageAnswer(DnsMessagePart):
    def __init__(self, message, name: typing.Union[DnsDomain, str] = None,
                 type: int = None, klass: int = None, ttl: int = None,
                 rdata: rdata.Rdata = None):
        self._message = message
        self.name = DnsDomain(message, label=name) if isinstance(name, str) else name
        self.type = type
        self.klass = klass
        self.ttl = ttl
        self.rdata = rdata

    @property
    def rdlength(self) -> int:
        return len(self.rdata.pack())

    @classmethod
    def unpack(cls, message: "DnsMessage", data: "ByteStream"):
        """Unpacks answer from bytes."""

        answer = cls(message)
        answer.name = DnsDomain.unpack(message, data)
        answer.type, answer.klass, answer.ttl, answer._rdlength = struct.unpack(
            "!HHLH", data.read(10)
        )
        answer.rdata = rdata.Rdata.by_type(answer.type).unpack(answer, data)
        return answer

    def pack(self):
        """Packs answer to bytes."""

        name = self.name.pack()
        fields = struct.pack("!HHLH", self.type, self.klass, self.ttl, self.rdlength)
        _rdata = self.rdata.pack()
        self._message.bytestream.write(fields + _rdata)

        return name + fields + _rdata
