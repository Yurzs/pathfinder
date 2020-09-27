from ipaddress import IPv4Address, IPv6Address

IPv4 = {
    "a.root-servers.net": IPv4Address("198.41.0.4"),
    "b.root-servers.net": IPv4Address("199.9.14.201"),
    "c.root-servers.net": IPv4Address("192.33.4.12"),
    "d.root-servers.net": IPv4Address("199.7.91.13"),
    "e.root-servers.net": IPv4Address("192.203.230.10"),
    "f.root-servers.net": IPv4Address("192.5.5.241"),
    "g.root-servers.net": IPv4Address("192.112.36.4"),
    "h.root-servers.net": IPv4Address("198.97.190.53"),
    "i.root-servers.net": IPv4Address("192.36.148.17"),
    "j.root-servers.net": IPv4Address("192.58.128.30"),
    "k.root-servers.net": IPv4Address("193.0.14.129"),
    "l.root-servers.net": IPv4Address("199.7.83.42"),
    "m.root-servers.net": IPv4Address("202.12.27.33"),
}

IPv6 = {
    "a.root-servers.net": IPv6Address("2001:503:ba3e::2:30"),
    "b.root-servers.net": IPv6Address("2001:500:200::b"),
    "c.root-servers.net": IPv6Address("2001:500:2::c"),
    "d.root-servers.net": IPv6Address("2001:500:2d::d"),
    "e.root-servers.net": IPv6Address("2001:500:a8::e"),
    "f.root-servers.net": IPv6Address("2001:500:2f::f"),
    "g.root-servers.net": IPv6Address("2001:500:12::d0d"),
    "h.root-servers.net": IPv6Address("2001:500:1::53"),
    "i.root-servers.net": IPv6Address("2001:7fe::53"),
    "j.root-servers.net": IPv6Address("2001:503:c27::2:30"),
    "k.root-servers.net": IPv6Address("2001:7fd::1"),
    "l.root-servers.net": IPv6Address("2001:500:9f::42"),
    "m.root-servers.net": IPv6Address("2001:dc3::35"),
}

ROOT_SERVERS = {domain: [address] for domain, address in IPv4.items()}
for domain, address in IPv6.items():
    ROOT_SERVERS[domain].append(address)
