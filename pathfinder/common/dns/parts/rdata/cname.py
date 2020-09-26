from pathfinder.common.dns.domains import DnsDomain
from pathfinder.common.dns.parts.rdata import Rdata


class Cname(Rdata):
    type = 5
    cname: DnsDomain

    @classmethod
    def unpack(cls, answer, data):

        cname = cls()
        cname.cname = DnsDomain.unpack(answer._message, data)
        return cname

    def pack(self):

        return self.cname.pack()
