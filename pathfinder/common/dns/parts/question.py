import struct

from pathfinder.common.dns.parts import DnsMessagePart
from pathfinder.common.dns.domains import DnsDomain


class DnsMessageQuestion(DnsMessagePart):
    """Dns question."""

    qname: DnsDomain
    qtype: int
    qclass: int

    def __init__(self, message, qname=None, qtype=None, qclass=None):
        self._message = message
        self.qname = DnsDomain(message, qname)
        self.qtype = qtype
        self.qclass = qclass

    def pack(self):
        """Packs question to bytes."""

        result = self.qname.pack()
        result += struct.pack("!H", self.qtype)
        result += struct.pack("!H", self.qclass)
        self._message.bytestream.write(struct.pack("!H", self.qtype) +
                                       struct.pack("!H", self.qclass))
        return result

    @classmethod
    def unpack(cls, message, data):
        """Unpacks question from bytes."""

        question = cls(message)
        question.qname = DnsDomain.unpack(message, data)
        question.qtype = struct.unpack("!H", data.read(2))[0]
        question.qclass = struct.unpack("!H", data.read(2))[0]
        return question
