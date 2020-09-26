import typing
from ipaddress import IPv4Address, IPv6Address

from pathfinder.common.manager import Manager, FoundNameservers
from pathfinder.common.dns.exceptions import DomainDoesntExist
from pathfinder.common.dns.message import DnsMessage
from pathfinder.common.dns.parts.rdata.rdata import Rdata
from pathfinder.common.dns.root_servers import ROOT_SERVERS
from pathfinder.common.protocol import Timeout


class ClientManager(Manager):
    protocol: typing.Union["TCPClientProtocol", "UDPClientProtocol"]

    @Manager.ip_version_filters
    async def resolve(self, resource_name, resource_type, ip_filter):
        """Resolves target using IPv4."""

        nameservers = await self.find_nameservers(resource_name, ip_filter=ip_filter)
        for nameserver in filter(ip_filter, nameservers):
            try:
                return await self.query(str(nameserver), resource_name, resource_type)
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

    async def _nameserver_resolve_many(self, domains, ip_filter):
        """Finds A and AAAA addresses of nameservers."""

        nameservers = []
        for domain in domains:
            message = await self.resolve(domain, Rdata.TYPE_A, ip_filter=ip_filter)
            for answer in message.answer.filter_resources():
                nameservers.append(answer.rdata.address)
            message = await self.resolve(domain, Rdata.TYPE_AAAA, ip_filter=ip_filter)
            for answer in message.answer.filter_resources():
                nameservers.append(answer.rdata.address)
        return nameservers

    async def _nameserver_request(
            self, server: typing.Union[IPv4Address, IPv6Address], resource_name, ip_filter):
        """Requests nameserver for resource_name."""

        response = await self.query(str(server), resource_name, Rdata.TYPE_NS)
        if response.answer.contains_type(Rdata.TYPE_NS):
            ns_domains = [answer.rdata.nsdname.lower() for answer in
                          response.answer]
            nameservers = self._find_in_additional(response, ns_domains,
                                                   [Rdata.TYPE_A, Rdata.TYPE_AAAA])
            if not nameservers:
                nameservers = await self._nameserver_resolve_many(ns_domains, ip_filter)
            raise FoundNameservers(nameservers)
        elif response.authority.contains_type(Rdata.TYPE_SOA):
            nameserver_domain = response.authority.filter_resources(type=Rdata.TYPE_SOA)[0].name
            nameservers = await self.find_nameservers(nameserver_domain, ip_filter=ip_filter)
            raise FoundNameservers(nameservers)
        elif response.authority.contains_name_type(resource_name, Rdata.TYPE_NS):
            ns_domains = [authority.rdata.nsdname.lower() for authority in
                          response.authority]
            nameservers = self._find_in_additional(response, ns_domains,
                                                   [Rdata.TYPE_A, Rdata.TYPE_AAAA])
            if not nameservers:
                nameservers = await self._nameserver_resolve_many(ns_domains, ip_filter)
            raise FoundNameservers(nameservers)
        elif response.authority.contains_type(Rdata.TYPE_NS):
            ns_domains = [authority.rdata.nsdname.lower() for authority in
                          response.authority]
            nameservers = self._find_in_additional(response, ns_domains,
                                                   [Rdata.TYPE_A, Rdata.TYPE_AAAA])
            if not nameservers:
                nameservers = await self._nameserver_resolve_many(ns_domains, ip_filter)
            return nameservers

    async def find_nameservers(self, resource_name, ip_filter):
        """Finds nameservers for resolve target."""

        nameservers = []
        for nameserver_address_list in ROOT_SERVERS.values():
            nameservers.extend(filter(ip_filter, nameserver_address_list))
        while filtered_nameservers:=list(filter(ip_filter, nameservers)):
            for server in filtered_nameservers:
                try:
                    nameservers = await self._nameserver_request(server, resource_name,
                                                                 ip_filter=ip_filter)
                    break
                except Timeout:
                    continue
                except FoundNameservers as found:
                    return found.nameservers

    async def query(self, host, resource_name, resource_type=Rdata.TYPE_A):
        """Creates message and sends it to host."""

        message = DnsMessage.new_question(resource_name, resource_type, 1)
        message = await self.encode_message(message)
        data = await self.protocol.send_new_message(self.loop, host, message)
        return await self.decode_message(data)
