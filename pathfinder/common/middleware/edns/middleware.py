import functools
from pathfinder.common.middleware.middleware import Middleware
from pathfinder.common.dns.message import DnsMessage
from pathfinder.common.middleware.edns.custom_answer import EdnsAnswer


class EDNSMiddleware(Middleware):

    def __init__(self, is_tcp=False, is_udp=True):
        self.is_tcp = is_tcp
        self.is_udp = is_udp

    @classmethod
    def before_decode(cls, func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            return await func(*args, **kwargs)
        return inner

    @classmethod
    def before_encode(cls, func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            return await func(*args, **kwargs)
        return inner
