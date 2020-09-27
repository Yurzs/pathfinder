import typing
from ipaddress import IPv4Address, IPv6Address

from pathfinder.common.manager import Manager, FoundNameservers
from pathfinder.common.dns.message import DnsMessage
from pathfinder.common.dns.parts.rdata.rdata import Rdata
from pathfinder.common.dns.root_servers import ROOT_SERVERS
from pathfinder.common.protocol import Timeout
from pathfinder.common.config import middlewares


class ClientManager(Manager):
    protocol: typing.Union["TCPClientProtocol", "UDPClientProtocol"]

    @Manager.ip_version_filters
    async def resolve(self, resource_name, resource_type, resource_class, ip_filter, timeout=1):
        """Resolves target using IPv4."""

        # TODO: maybe pass single search instance with request params in it?

        nameservers = await self.find_nameservers(resource_name, resource_class,
                                                  ip_filter=ip_filter)
        for nameserver in filter(ip_filter, nameservers):
            try:
                return await self.query(str(nameserver),
                                        resource_name,
                                        resource_type,
                                        resource_class,
                                        timeout=timeout)
            except Timeout:
                continue

    @staticmethod
    def _find_in_additional(message, names, types):
        """Finds additional data for names."""

        result = []
        for _type in types:
            if message.additional.contains_type(_type):
                for additional in message.additional.filter_resources(type=_type):
                    if additional.name.lower() in names:
                        result.append(additional.rdata.address)
        return result

    async def _nameserver_resolve_many(self, domains, resource_class, ip_filter):
        """Finds A and AAAA addresses of nameservers."""

        nameservers = []
        for domain in domains:
            message = await self.resolve(domain, Rdata.TYPE_A, resource_class,
                                         ip_filter=ip_filter)
            for answer in message.answer.filter_resources():
                nameservers.append(answer.rdata.address)
            message = await self.resolve(domain, Rdata.TYPE_AAAA, resource_class,
                                         ip_filter=ip_filter)
            for answer in message.answer.filter_resources():
                nameservers.append(answer.rdata.address)
        return nameservers

    async def _nameserver_request(
            self, server: typing.Union[IPv4Address, IPv6Address], resource_name,
            resource_class, ip_filter):
        """Requests nameserver for resource_name."""

        response = await self.query(str(server), resource_name, Rdata.TYPE_NS, resource_class)
        if response.answer.contains_type(Rdata.TYPE_NS):
            ns_domains = [answer.rdata.nsdname.lower() for answer in
                          response.answer]
            nameservers = self._find_in_additional(response, ns_domains,
                                                   [Rdata.TYPE_A, Rdata.TYPE_AAAA])
            if not nameservers:
                nameservers = await self._nameserver_resolve_many(ns_domains, resource_class,
                                                                  ip_filter=ip_filter)
            raise FoundNameservers(nameservers)
        elif response.authority.contains_type(Rdata.TYPE_SOA):
            nameserver_domain = response.authority.filter_resources(type=Rdata.TYPE_SOA)[
                0].name.label
            nameservers = await self.find_nameservers(nameserver_domain, resource_class,
                                                      ip_filter=ip_filter)
            raise FoundNameservers(nameservers)
        elif response.authority.contains_name_type(resource_name, Rdata.TYPE_NS):
            ns_domains = [authority.rdata.nsdname.lower() for authority in
                          response.authority]
            nameservers = self._find_in_additional(response, ns_domains,
                                                   [Rdata.TYPE_A, Rdata.TYPE_AAAA])
            if not nameservers:
                nameservers = await self._nameserver_resolve_many(ns_domains, resource_class,
                                                                  ip_filter=ip_filter)
            raise FoundNameservers(nameservers)
        elif response.authority.contains_type(Rdata.TYPE_NS):
            ns_domains = [authority.rdata.nsdname.lower() for authority in
                          response.authority]
            nameservers = self._find_in_additional(response, ns_domains,
                                                   [Rdata.TYPE_A, Rdata.TYPE_AAAA])
            if not nameservers:
                nameservers = await self._nameserver_resolve_many(ns_domains, resource_class,
                                                                  ip_filter=ip_filter)
            return nameservers

    async def find_nameservers(self, resource_name, resource_class, ip_filter):
        """Finds nameservers for resolve target."""

        nameservers = []
        for nameserver_address_list in ROOT_SERVERS.values():
            nameservers.extend(filter(ip_filter, nameserver_address_list))
        while filtered_nameservers:=list(filter(ip_filter, nameservers)):
            for server in filtered_nameservers:
                try:
                    nameservers = await self._nameserver_request(server, resource_name,
                                                                 resource_class,
                                                                 ip_filter=ip_filter)
                    break
                except Timeout:
                    continue
                except FoundNameservers as found:
                    return found.nameservers

    @middlewares.on_query
    async def query(self, host, resource_name, resource_type, resource_class, timeout=1):
        """Creates message and sends it to host."""

        message = DnsMessage.new_question(resource_name, resource_type, resource_class)
        message = await self.encode_message(message)
        data = await self.protocol.send_new_message(self.loop, host, message, timeout=timeout)
        return await self.decode_message(data)
