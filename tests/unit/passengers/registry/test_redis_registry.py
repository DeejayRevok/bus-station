from unittest import TestCase
from unittest.mock import Mock

from redis import Redis

from bus_station.command_terminal.command import Command
from bus_station.passengers.registry.redis_passenger_record_repository import RedisRegistry


class TestRedisRegistry(TestCase):
    def setUp(self) -> None:
        self.redis_mock = Mock(spec=Redis)
        self.redis_registry = RedisRegistry(self.redis_mock)

    def test_register(self):
        test_command = Mock(spec=Command)
        test_destination = "test_destination"

        self.redis_registry.register_destination(test_command.__class__, test_destination)

        self.redis_mock.set.assert_called_once_with(test_command.__class__.__name__, test_destination.encode("UTF-8"))

    def test_get_passenger_destination(self):
        test_command = Mock(spec=Command)
        test_destination = "test_destination"
        self.redis_mock.get.return_value = test_destination.encode("UTF-8")

        destination = self.redis_registry.get_passenger_destination(test_command.__class__)

        self.redis_mock.get.assert_called_once_with(test_command.__class__.__name__)
        self.assertEqual(test_destination, destination)

    def test_unregister(self):
        test_command = Mock(spec=Command)

        self.redis_registry.unregister(test_command.__class__)

        self.redis_mock.delete.assert_called_once_with(test_command.__class__.__name__)
