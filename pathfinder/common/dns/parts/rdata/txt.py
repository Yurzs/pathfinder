from pathfinder.common.dns.parts.rdata import Rdata


class Txt(Rdata):
    txt_data: str
    type = 16

    @classmethod
    def unpack(cls, answer, data):

        txt = cls()
        txt._txt_length = data.read(1)
        txt.txt_data = data.read(answer._rdlength - 1).decode("ascii")
        return txt

    def pack(self):
        packed = len(self.txt_data.encode("ascii")).to_bytes(1, "big")
        packed += self.txt_data.encode("ascii")
        return packed
