from typing import ClassVar
from unittest import TestCase


class IntegrationTestCase(TestCase):
    rabbitmq: ClassVar[dict] = {"user": "guest", "password": "guest", "host": "rabbitmq", "port": 5672}
    redis: ClassVar[dict] = {"host": "redis", "port": 6379}
    postgres: ClassVar[dict] = {
        "host": "postgres",
        "port": 5432,
        "user": "test_user",
        "password": "test_password",
        "db": "test_db",
    }
    mongo: ClassVar[dict] = {
        "host": "mongo",
        "port": 27017,
        "user": "test_user",
        "password": "test_password",
        "db": "test_db",
    }
