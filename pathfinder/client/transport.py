

class DNSMessageTransport:
    def __init__(self, transport):
        self._transport = transport

    def write(self, message):
        """Encodes message to bytes then sends it to transport."""

        self._transport.write(bytes(message))
