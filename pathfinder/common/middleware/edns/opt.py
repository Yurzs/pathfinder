#  Copyright (c) Yurzs 2019.
import struct
from pathfinder.common.dns.parts.rdata import Rdata


class Opt(Rdata):
    """Pseudo RR type for EDNS."""

    type = 41

    @classmethod
    def unpack(cls, answer, data: 'ByteStream'):
        """Unpacks OPT RR from bytes."""

        opt = cls()
        opt._answer = answer
        rdata_len = int(opt._answer._rdlength)
        while rdata_len:
            if data.peek(2):
                option_code = struct.unpack("!H", data.read(2))[0]
                option_length = struct.unpack("!H", data.read(2))[0]
                setattr(opt, str(option_code), data.read(option_length))
                rdata_len -= 4 - option_length
            else:
                break
        return opt

    def pack(self):
        """Packs pseudo-RR to bytes."""

        packed = b""
        for attr, value in self.__dict__.items():
            if attr.startswith("_"):
                continue
            packed += struct.pack("!2H", int(attr), len(value))
            packed += value
        return packed
