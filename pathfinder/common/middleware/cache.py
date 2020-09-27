import functools

from pathfinder.common.middleware.middleware import Middleware
from pathfinder.common.dns.message import DnsMessage
from pathfinder.common.dns.parts.rdata.rdata import Rdata


class CacheMiddleware(Middleware):
    STORAGE = {}
    AUTHORITY_RESOURCE = [Rdata.TYPE_NS, Rdata.TYPE_SOA]

    @classmethod
    def _parse_and_save_message(cls, message):
        """Parses message insides then saves them to storage."""

        for part_name in ("answer", "authority", "additional"):
            part = getattr(message, part_name)
            for resource in part:
                cls.STORAGE.setdefault(resource.name.label.lower(), {})
                storage_domain = cls.STORAGE[resource.name.label.lower()]
                storage_domain.setdefault(resource.type, {})
                storage_type = storage_domain[resource.type]
                storage_type.setdefault(resource.klass, [])
                storage_class = storage_type[resource.klass]
                if not cls._check_storage_contains(storage_class, resource):
                    storage_class.append(resource)

    @classmethod
    def purge_expired(cls):
        """Removes expired resources from cache."""

        for rrtype in cls.STORAGE.values():
            for rrclass in rrtype.values():
                for resource_storage in rrclass.values():
                    for resource in resource_storage.copy():
                        if resource.expired:
                            resource_storage.remove(resource)

    @classmethod
    def _add_additional(cls, message):
        """Adds additional info for domains in message."""

        for domain in message.used_domains:
            domain = domain.lower()
            if list(filter(lambda r: r.name == domain and
                                     r.type in [Rdata.TYPE_A, Rdata.TYPE_AAAA], message.answer)):
                continue
            else:
                # TODO: keep class from original domain holder answer
                for rrtype in (Rdata.TYPE_A, Rdata.TYPE_AAAA):
                    filtered_storage = filter(lambda r: not r.expired,
                                              cls.STORAGE.get(domain, {}).get(
                                                  rrtype, {}).get(1, []))
                    for resource in filtered_storage:
                        resource.message = message
                        resource.ttl = resource.ttl_left
                        message.additional.append(resource)

    @classmethod
    def _find_resources(cls, resource_name, resource_type, resource_class):
        """Finds still active resources in storage. Deletes old ones if finds."""

        cls.purge_expired()
        result_message = DnsMessage.new_question(resource_name, resource_type, resource_class)
        filtered_storage = filter(lambda r: not r.expired,
                                  cls.STORAGE.get(resource_name, {}).get(
                                      resource_type, {}).get(
                                      resource_class, []))
        for resource in filtered_storage:
            resource.ttl = resource.ttl_left
            if resource.type in cls.AUTHORITY_RESOURCE:
                result_message.authority.append(resource)
            else:
                result_message.answer.append(resource)
        cls._add_additional(result_message)
        return result_message

    @staticmethod
    def _check_storage_contains(storage, resource):
        """Checks that resource storage already contains resource."""

        for element in storage:
            if element.name != resource.name:
                continue
            elif element.type != resource.type:
                continue
            elif element.rdata != resource.rdata:
                continue
            return True
        return False

    @classmethod
    async def regular_query_and_save(cls, func, *args, **kwargs):
        result = await func(*args, **kwargs)
        if isinstance(result, DnsMessage):
            cls._parse_and_save_message(result)
        return result

    @classmethod
    def on_query(cls, func):
        @functools.wraps(func)
        async def wrap(manager, host, resource_name, resource_type, resource_class, *args,
                       **kwargs):
            cached_message = cls._find_resources(resource_name, resource_type, resource_class)
            if not cached_message.answer and \
                    not cached_message.authority and \
                    not cached_message.authority:
                return await cls.regular_query_and_save(
                    func, manager, host, resource_name, resource_type, resource_class, *args,
                    **kwargs
                )
            return cached_message
        return wrap
