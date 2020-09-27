import functools
import typing
from abc import ABCMeta


class StopMiddlewareIteration(BaseException):
    def __init__(self, result):
        self.result = result


class Middleware(metaclass=ABCMeta):
    outer_container: "MiddlewareList"

    @classmethod
    def before_decode(cls, func):
        """Helps to decode message. Called before message decoding."""

        @functools.wraps(func)
        def wrap(*args, **kwargs):
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
        def wrap(*args, **kwargs):
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

    @classmethod
    def on_query(cls, func):
        @functools.wraps(func)
        def wrap(manager, host, resource_name, resource_type, resource_class, *args, **kwargs):
            return func(
                manager, host, resource_name, resource_type, resource_class, *args, **kwargs)
        return wrap


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

    def on_query(self, func):
        nested = func
        for middleware in self.middlewares:
            nested = middleware.on_query(nested)

        @functools.wraps(func)
        def wrap(manager, host, resource_name, resource_type, resource_class=1, **kwargs):
            try:
                return nested(manager, host, resource_name, resource_type, resource_class,
                              **kwargs)
            except StopMiddlewareIteration as stop:
                return stop.result

        return wrap
