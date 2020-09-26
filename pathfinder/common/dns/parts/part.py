from abc import abstractmethod

from pathfinder.common.dns.domains import DnsDomain


class DnsMessagePart:
    """Base part class."""

    @abstractmethod
    def pack(self):
        """Packs message part to bytes."""

    @classmethod
    @abstractmethod
    def unpack(cls, message, data):
        """Unpacks message part from bytes."""

    def to_dict(self):
        """Returns dict representation of dns message part."""

        part_dict = {}
        for k, v in {attr: val for attr, val in self.__dict__.items()
                     if not attr.startswith("_")}.items():
            if isinstance(v, DnsDomain):
                part_dict[k] = v.label
            elif hasattr(v, "to_dict"):
                part_dict[k] = v.to_dict()
            else:
                part_dict[k] = v
        return part_dict
