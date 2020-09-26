class DnsException(BaseException):
    pass


class MalformedPacket(DnsException):
    pass


class DomainDoesntExist(DnsException):
    def __init__(self, message):
        self.message = message
