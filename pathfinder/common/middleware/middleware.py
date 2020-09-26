import functools
import typing
from abc import ABCMeta, abstractmethod


class Middleware(metaclass=ABCMeta):
    outer_container: "MiddlewareList"

    @classmethod
    def before_decode(cls, func):
        """Helps to decode message. Called before message decoding."""

        @functools.wraps(func)
        async def wrap(*args, **kwargs):
            return func(*args, **kwargs)
        return wrap

    @classmethod
    async def after_decode(cls, message: "DnsMessage"):
        """Helps to decode message. Called after message decoding."""

        return message

    @classmethod
    def before_encode(cls, func):
        """Help to encode message. Called before message encoding."""

        @functools.wraps(func)
        async def wrap(*args, **kwargs):
            return func(*args, **kwargs)
        return wrap

    @classmethod
    async def after_encode(cls, data: bytes):
        """Help to encode message. Called after message encoding."""

        return data

    @staticmethod
    async def _check_if_coroutine_and_await(obj):
        if isinstance(obj, typing.Coroutine):
            return await obj
        else:
            return obj


class MiddlewareList:
    def __init__(self, *middlewares: Middleware):
        for middleware in middlewares:
            middleware.outside_container = self
        self.middlewares = middlewares

    def on_encode(self, func):
        nested = func
        for middleware in self.middlewares:
            nested = middleware.before_encode(nested)

        @functools.wraps(func)
        async def wrap(*args, **kwargs):
            result = await nested(*args, **kwargs)
            for mware in self.middlewares:
                result = await mware.after_encode(result)
            return result
        return wrap

    def on_decode(self, func):
        """Nests middlewares on_decode methods."""

        nested = func
        for middleware in self.middlewares:
            nested = middleware.before_decode(nested)

        @functools.wraps(func)
        async def wrap(*args, **kwargs):
            result = await nested(*args, **kwargs)
            for mware in self.middlewares:
                await mware.after_decode(result)
            return result
        return wrap
