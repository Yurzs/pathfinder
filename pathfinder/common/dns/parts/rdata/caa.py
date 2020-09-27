import struct

from pathfinder.common.dns.exceptions import DnsException
from pathfinder.common.dns.parts.rdata import Rdata


class Caa(Rdata):
    type = 257

    critical: bool
    tag: str
    value: str

    @classmethod
    def unpack(cls, answer, data):
        """Unpacks CAA RR from bytes."""

        caa = cls()
        caa.critical = struct.unpack("!?", data.read(1))[0]
        tag_length = struct.unpack("!B", data.read(1))[0]
        caa.tag = data.read(tag_length).decode("ascii")
        caa.value = data.read(answer._rdlength - 2 - tag_length).decode('ascii')

        return caa

    def pack(self):
        """Packs CAA RR to bytes."""

        packed = b""
        if self.tag not in ("issue", "issuewild", "iodef"):
            raise DnsException("Wrong CAA tag value")
        packed += struct.pack("!?", self.critical)
        tag_length = len(self.tag.encode("ascii"))
        packed += struct.pack("!B", tag_length) + self.tag.encode("ascii")
        packed += self.value.encode("ascii")

        return packed
