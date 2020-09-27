#  Copyright (c) Yurzs 2019.

import struct

from pathfinder.common.dns.domains import DnsDomain
from pathfinder.common.dns.parts import DnsMessageAnswer, rdata
from pathfinder.common.middleware.edns.opt import Opt


class EdnsAnswer(DnsMessageAnswer):
    """Custom Answer type for ENDS."""

    name: DnsDomain
    type: int
    klass: int
    ttl: int
    rdlength: int
    rdata: rdata.Rdata

    def __init__(self, message, udp_payload_size=None, extended_rcode=None,
                 version=None, do=None, z=None, rdata=None):
        self._message = message
        self.name = DnsDomain(message, label="", can_be_shortened=False)
        self.type = 41
        self.udp_payload_size = udp_payload_size
        self.extended_rcode = extended_rcode
        self.version = version
        self.do = do
        self.z = z
        opt = Opt()
        opt._answer = self
        self.rdata = rdata if rdata else opt

    @property
    def ttl(self):
        return int.from_bytes(
            struct.pack("!BBH", self.extended_rcode, self.version, self.do * 32768 + self.z),
            "big")

    @property
    def rdlength(self):
        return len(self.rdata.pack())

    @classmethod
    def unpack(cls, message, data):
        answer = cls(message)
        answer.name = DnsDomain.unpack(message, data)
        answer.type, answer.udp_payload_size, answer.extended_rcode, answer.version, ttl_octet2, \
        answer._rdlength = struct.unpack(
            "!2H2B2H", data.read(10)
        )
        answer.do = True if ttl_octet2 >= 32768 else False
        answer.z = ttl_octet2 - 32768 if answer.do else ttl_octet2
        answer.rdata = rdata.Rdata.by_type(answer.type).unpack(answer, data)
        return answer

    def pack(self):
        name = self.name.pack()
        fields = struct.pack("!HHLH", self.type, self.udp_payload_size, self.ttl, self.rdlength)
        rdata_ = self.rdata.pack()
        self._message.bytestream.write(fields + rdata_)

        return name + fields + rdata_
