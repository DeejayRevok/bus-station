from unittest import TestCase

import pytest

from bus_station.command_terminal.command import Command
from bus_station.passengers.registry.redis_registry import RedisRegistry


class CommandTest(Command):
    pass


@pytest.mark.usefixtures("rabbitmq", "redis")
class TestRedisRegistry(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_env_ready = False
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.test_env_ready = True

    def setUp(self) -> None:
        self.redis_registry = RedisRegistry(self.redis_host, self.redis_port)

    def test_register(self):
        test_destination = "test_destination"

        self.redis_registry.register(CommandTest, test_destination)

        self.assertEqual(test_destination, self.redis_registry.get_passenger_destination(CommandTest))

    def test_unregister(self):
        test_destination = "test_destination"
        self.redis_registry.register(CommandTest, test_destination)

        self.redis_registry.unregister(CommandTest)

        self.assertIsNone(self.redis_registry.get_passenger_destination(CommandTest))
