import asyncio

from pathfinder.common.protocol import ProtoBase


class TCPClientProtocol(asyncio.Protocol, ProtoBase):
    def __init__(self, loop, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = loop
        self.message = message
        self.connection_lost_future = asyncio.Future()
        self.response_message = asyncio.Future()

    @ProtoBase.make_async
    async def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:
        """Sends message to destination"""

        self.transport = transport
        transport.write(self.message)

    @ProtoBase.make_async
    async def data_received(self, data: bytes) -> None:
        """Parses incoming dns message."""

        self.response_message.set_result(data)

    def connection_lost(self, exc) -> None:
        self.transport.close()
        self.connection_lost_future.set_result(True)

    @classmethod
    async def send_new_message(cls, loop, host, data: bytes, port=53):
        transport, protocol = await loop.create_connection(
            lambda: cls(loop, data),
            host, port
        )

        await protocol.response_message
        return protocol.response_message.result()
