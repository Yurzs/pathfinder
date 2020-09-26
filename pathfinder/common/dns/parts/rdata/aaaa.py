import ipaddress

from pathfinder.common.dns.parts.rdata import Rdata


class Aaaa(Rdata):
    address: ipaddress.IPv6Address
    type = 28

    @classmethod
    def unpack(cls, answer, data):
        """Unpacks AAAA RR from byte format."""

        aaaa = cls()
        aaaa.address = ipaddress.IPv6Address(data.read(answer._rdlength))
        return aaaa

    def pack(self):
        """Packs AAAA RR to bytes."""

        return int(self.address).to_bytes(16, "big")
