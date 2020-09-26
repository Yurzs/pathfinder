import asyncio
import functools
from abc import ABCMeta, abstractmethod


class Timeout(BaseException):
    pass


class ProtoBase(metaclass=ABCMeta):
    @staticmethod
    def make_async(func):
        @functools.wraps(func)
        async def async_wrap(protocol, data):
            return await func(protocol, data)

        @functools.wraps(func)
        def wrap(protocol, data):
            return asyncio.Task(async_wrap(protocol, data), loop=protocol.loop)
        return wrap

    @classmethod
    @abstractmethod
    async def send_new_message(cls, loop, host: str, data: bytes, port: int = 53):
        """Creates new protocol instance and sends message."""
