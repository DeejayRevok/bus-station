from typing import ClassVar
from unittest import TestCase


class IntegrationTestCase(TestCase):
    rabbitmq: ClassVar[dict] = {"user": "guest", "password": "guest", "host": "rabbitmq", "port": 5672}
    redis: ClassVar[dict] = {"host": "redis", "port": 6379}
    kafka: ClassVar[dict] = {"host": "kafka", "port": 29092}
