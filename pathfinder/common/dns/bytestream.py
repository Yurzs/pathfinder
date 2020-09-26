class ByteStream:
    def __init__(self, data: bytes = b""):
        if not isinstance(data, bytes):
            raise ValueError("Data can only be bytes")
        self.data = data
        self.pos = 0

    def read(self, length=None):
        """Reads and moves cursor to new position"""

        if not length:
            if self.pos == len(self.data):
                raise MemoryError("All data have been read, nothing here anymore.")
            data = self.data[self.pos:]
            self.pos = len(self.data)
            return data
        if self.pos + length > len(self.data):
            raise MemoryError("Cursor cant move above data length.")
        result = self.data[self.pos: self.pos + length]
        self.pos += length
        return result

    def peek(self, length=None):
        """Reads without moving cursor to new position"""

        if not length:
            return self.data[self.pos:]
        return self.data[self.pos: self.pos + length]

    def write(self, data: bytes) -> None:
        """Adds new bytes to data."""

        self.data += data
        self.pos = len(self.data)

    def reset(self):
        """Resets cursor to default position"""

        self.pos = 0

    def clear(self):
        """Clears all data and moves cursor to starting position."""

        self.data = b""
        self.pos = 0
