from pathfinder.common.dns.domains import DnsDomain
from pathfinder.common.dns.parts.rdata import Rdata


class Ns(Rdata):
    nsdname: DnsDomain
    type = 2

    @classmethod
    def unpack(cls, answer, data):

        ns = cls()
        ns.nsdname = DnsDomain.unpack(answer._message, data)
        return ns

    def pack(self):

        return self.nsdname.pack()
