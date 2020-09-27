import asyncio

from pathfinder.common.manager import Manager

from pathfinder.common.protocol import ProtoBase, Timeout


class UDPClientProtocol(asyncio.DatagramProtocol, ProtoBase):
    def __init__(self, loop, message, timeout=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = loop
        self.message = message
        self.response_message = asyncio.Future()
        self.loop.create_task(self.wait_timeout(timeout))

    async def wait_timeout(self, timeout):
        await asyncio.sleep(timeout)
        if not self.response_message.done():
            self.response_message.set_exception(Timeout())

    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:

        self.transport = transport
        self.transport.sendto(self.message)

    def datagram_received(self, data, addr) -> None:
        self.response_message.set_result(data)

    def connection_lost(self, exc) -> None:
        self.transport.close()

    @classmethod
    async def send_new_message(cls, loop, host: str, data: bytes, port: int = 53, timeout=1):

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: cls(loop, data, timeout=timeout),
            remote_addr=(host, port)
        )

        await protocol.response_message
        return protocol.response_message.result()
