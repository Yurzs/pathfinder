import struct

from pathfinder.common.dns.domains import DnsDomain
from pathfinder.common.dns.parts.rdata import Rdata


class Soa(Rdata):
    type = 6

    mname: DnsDomain
    rname: DnsDomain
    serial: int
    refresh: int
    retry: int
    expire: int
    minimum: int

    @classmethod
    def unpack(cls, answer, data):

        soa = cls()
        soa.mname = DnsDomain.unpack(answer._message, data)
        soa.rname = DnsDomain.unpack(answer._message, data)
        soa.serial, soa.refresh, soa.retry, soa.expire, soa.minimum = struct.unpack(
            "!LLLLL", data.read(20))
        return soa
    
    def pack(self):
        packed = self.mname.pack()
        packed += self.rname.pack()
        packed += struct.pack("!LLLLL", self.serial, self.refresh, self.retry,
                              self.expire, self.minimum)
        return packed
