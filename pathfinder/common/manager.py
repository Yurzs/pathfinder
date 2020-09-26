import asyncio
import functools
from ipaddress import IPv6Address, IPv4Address

from pathfinder.common.dns.message import DnsMessage
from pathfinder.common.dns.parts.rdata.rdata import Rdata
from pathfinder.common.config import middlewares


class FoundNameservers(BaseException):
    def __init__(self, nameservers):
        self.nameservers = nameservers


class Manager:
    def __init__(self, loop, protocol_cls, destination=""):
        self.loop = loop
        self.protocol = protocol_cls
        self.destination = destination

    def set_target(self, destination):
        self.destination = destination

    @staticmethod
    def ip_version_filters(func):
        @functools.wraps(func)
        def wrap(cls, *args, ip_versions=(4, 6), **kwargs):
            def _filter(address):
                return isinstance(address, (IPv4Address, IPv6Address))

            def _filter4(address):
                return isinstance(address, IPv4Address)

            def _filter6(address):
                return isinstance(address, IPv6Address)

            if kwargs.get("ip_filter") is None:
                if 4 in ip_versions and 6 in ip_versions:
                    ip_filter = _filter
                elif 4 in ip_versions:
                    ip_filter = _filter4
                elif 6 in ip_versions:
                    ip_filter = _filter6
                else:
                    raise Exception(f"Unknown IP version {ip_versions}")
                return func(cls, *args, ip_filter=ip_filter, **kwargs)
            return func(cls, *args, **kwargs)
        return wrap

    @middlewares.on_decode
    async def decode_message(self, data):
        return DnsMessage.unpack(data)

    @middlewares.on_encode
    async def encode_message(self, message: DnsMessage):
        return message.pack()
