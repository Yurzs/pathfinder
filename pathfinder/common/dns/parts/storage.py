from collections import UserList

from pathfinder.common.dns.exceptions import DnsException
from pathfinder.common.dns.parts import DnsMessagePart


class DnsPartStorage(UserList):

    def append(self, object) -> None:
        if not isinstance(object, DnsMessagePart):
            raise DnsException("Cant append anything other than dns message part.")
        super().append(object)

    def pack(self):
        result = b""
        for item in self:
            result += item.pack()
        return result

    def __repr__(self):
        string = ""
        for item in self:
            string += f"{item}\n"
        return string

    def to_dict(self):
        """Return dict representation of items in storage."""

        return [i.to_dict() for i in self]

    def contains_type(self, klass):
        """Checks that storage contains specific rdata type."""

        if isinstance(klass, int):
            return bool(list(filter(lambda item: item.type == klass, self)))
        else:
            return bool(list(filter(lambda item: isinstance(item.rdata, klass), self)))

    def contains_name_type(self, name, klass):
        """Checks that storage contains specific rdata type."""

        if isinstance(klass, int):
            return bool(list(filter(
                lambda item: item.type == klass and item.name.lower() == name.lower(), self)))
        else:
            return bool(list(filter(
                lambda item: isinstance(item.rdata, klass) and item.name.lower() == name.lower(),
                self)))

    def filter_resources(self, **kwargs):
        """Filters storage resources."""

        resources = self.data
        for field, value in kwargs.items():
            resources = list(filter(lambda item: getattr(item, field, None) == value, resources))
        return resources
