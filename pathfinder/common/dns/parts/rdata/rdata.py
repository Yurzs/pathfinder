import ipaddress

from pathfinder.common.dns.domains import DnsDomain


class Rdata:
    TYPE_A = 1
    TYPE_AAAA = 28
    TYPE_CAA = 257
    TYPE_CNAME = 5
    TYPE_MX = 15
    TYPE_NS = 2
    TYPE_PTR = 12
    TYPE_SOA = 6
    TYPE_TXT = 16

    type: int

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__class__.__annotations__:
                value_type = self.__class__.__annotations__[key]
                setattr(self, key, value_type(value))

    @classmethod
    def by_type(cls, type):
        for rrtype in cls.__subclasses__():
            if rrtype.type == type:
                return rrtype

    def pack(self):
        pass

    @classmethod
    def unpack(cls, answer, data):
        pass

    def __repr__(self):
        # name_len = len(self.__class__.__name__)
        # if (30 - 6 - name_len) % 2 == 1:
        #     fillers = (
        #         ("*" * int((27 - 6 - name_len) / 2) + " ",
        #          "*" * int((27 - 6 - name_len) / 2)))
        # else:
        #     fillers = ["-" * int((27 - 6 - name_len) / 2)] * 2
        #
        string = ""
        # string = f"{fillers[0]}{self.__class__.__name__.upper()}{fillers[1]}\n"
        for k, v in {attr: val for attr, val in self.__dict__.items()
                     if not attr.startswith("_")}.items():
            string += f"{k.upper()}: {v}\n"
        # string += f"{'*' * 24}"
        return string

    def __repr_chunks__(self):
        """Return chunked representation of fields. For recipe-like message view."""

        chunks = []

        name_len = len(self.__class__.__name__)
        if (30 - 2 - name_len) % 2 == 1:
            fillers = (
                ("*" * int((30 - 2 - name_len) / 2) + " ",
                 "*" * int((30 - 2 - name_len) / 2)))
        else:
            fillers = ["*" * int((30 - 2 - name_len) / 2)] * 2

        chunks.append(f"{fillers[0]}{self.__class__.__name__.upper()}{fillers[1]}")

        for k, v in {attr: val for attr, val in self.__dict__.items()
                     if not attr.startswith("_")}.items():
            if len(f"{k.upper()}: {v}") > 28:
                start_pos = 28 - len(k.upper()) - 2
                chunks.append(f"{k.upper()}: {str(v)[:start_pos]}")
                for chunk in [str(v)[start: start + 28]
                              for start in range(start_pos, len(str(v)), 28)]:
                    if len(chunk) < 29:
                        chunk = chunk + " " * (28 - len(chunk))
                        chunks.append(chunk)
                    else:
                        chunks.append(chunk)
            elif len(f"{k.upper()}: {v}") < 28:
                chunks.append(f"{k.upper()}: {v}" + " " * (28 - len(f"{k.upper()}: {v}")))
            else:
                chunks.append(f"{k.upper()}: {v}")
        chunks.append("*"*28)

        return chunks

    def to_dict(self):
        """Returns dict representation of rdata object."""

        rdata_dict = {}
        for k, v in {attr: val for attr, val in self.__dict__.items()
                     if not attr.startswith("_")}.items():
            if isinstance(v, DnsDomain):
                rdata_dict[k] = v.label
            elif isinstance(v, ipaddress.IPv4Address) or isinstance(v, ipaddress.IPv6Address):
                rdata_dict[k] = str(v)
            else:
                rdata_dict[k] = v
        return rdata_dict

    def __eq__(self, other):
        """Checks that RRs are the same."""

        if not isinstance(other, Rdata):
            return False
        return other.to_dict() == self.to_dict()
