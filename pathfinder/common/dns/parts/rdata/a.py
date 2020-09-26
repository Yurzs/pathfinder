import ipaddress
import struct

from pathfinder.common.dns.parts.rdata import Rdata


class A(Rdata):
    address: ipaddress.IPv4Address
    type = 1

    @classmethod
    def unpack(cls, answer, data):

        a = cls()
        a.address = ipaddress.IPv4Address(struct.unpack("!L", data.read(answer._rdlength))[0])
        return a

    def pack(self):

        return struct.pack("!L", int(self.address))
