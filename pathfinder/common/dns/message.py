import json
import random
from collections import OrderedDict

import pathfinder.common.dns.parts as message_parts

from pathfinder.common.dns.exceptions import MalformedPacket
from pathfinder.common.dns.domains import DomainStorage
from pathfinder.common.dns.bytestream import ByteStream
from pathfinder.common.dns.parts import DnsMessageQuestion, DnsMessageHeader


class DnsMessage:
    def __init__(self, header=None, question=None, answer=None, authority=None, additional=None):

        self.header = message_parts.header.DnsMessageHeader(self)
        self.question = message_parts.DnsPartStorage()
        self.answer = message_parts.DnsPartStorage()
        self.authority = message_parts.DnsPartStorage()
        self.additional = message_parts.DnsPartStorage()
        self.domains = DomainStorage()
        self.bytestream = ByteStream()

    @classmethod
    def unpack(cls, data: bytes):
        """Unpacks dns message from bytes."""

        data = ByteStream(data)
        message = cls()

        message.header = message_parts.DnsMessageHeader.unpack(message, data.read(12))

        unpack_order = [
            (message_parts.DnsMessageQuestion, message.question, message.header._qdcount),
            (message_parts.DnsMessageAnswer, message.answer, message.header._ancount),
            (message_parts.DnsMessageAnswer, message.authority, message.header._nscount),
            (message_parts.DnsMessageAnswer, message.additional, message.header._arcount)
        ]
        for part in unpack_order:
            data = message.parse_resource_record(message, *part, data)

        if len(data.peek()) != 0:
            raise MalformedPacket()
        return message

    @staticmethod
    def parse_resource_record(message, rrtype, storage, count, data):
        """Parses resource record (answer, authority, additional) from bytes."""

        for rr in range(count):
            storage.append(rrtype.unpack(message, data))
        return data

    def pack(self):
        """Packs dns message to bytes."""

        self.bytestream.clear()
        self.domains.clear()
        result = b""
        self.header.pack()
        result += self.question.pack()
        result += self.answer.pack()
        result += self.authority.pack()
        result += self.additional.pack()
        return self.bytestream.data

    def to_dict(self):
        """Returns JSON representation of dns message."""

        return OrderedDict([
            ("header", self.header.to_dict()),
            ("question", self.question.to_dict()),
            ("answer", self.answer.to_dict()),
            ("authority", self.authority.to_dict()),
            ("additional", self.additional.to_dict()),
        ])

    @classmethod
    def new_question(cls, label, type, klass):
        """Create question message."""

        message = cls()
        header = DnsMessageHeader(message)
        header.id = random.randrange(1, 65535)
        header.qr = 0
        header.opcode = 0
        header.aa = 1
        header.tc = 0
        header.rd = 1
        header.ra = 0
        header.z = 0
        header.rcode = 0
        message.header = header
        question = DnsMessageQuestion(message, label, type, klass)
        message.question.append(question)
        return message

    @classmethod
    def dummy_answer(cls, answers: list, label, type, klass):
        """Creates fake answer for question."""

        message = cls.new_question(label, type, klass)

        message.header.qr = True
        message.additional.clear()

        for answer in answers:
            message.answer.append(answer)

        return message

    def to_json(self) -> str:
        """Return pretty JSON representation of dns message."""

        return json.dumps(self.to_dict(), indent=4)
