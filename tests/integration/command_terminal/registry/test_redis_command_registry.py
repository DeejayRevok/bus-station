from dataclasses import dataclass

from redis import Redis

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.redis_command_registry import RedisCommandRegistry
from bus_station.passengers.registry.in_memory_passenger_record_repository import InMemoryPassengerRecordRepository
from bus_station.passengers.registry.redis_passenger_record_repository import RedisPassengerRecordRepository
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def handle(self, command: CommandTest) -> None:
        pass


class TestRedisCommandRegistry(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_env_ready = False
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)
        cls.test_env_ready = True

    def setUp(self) -> None:
        self.in_memory_repository = InMemoryPassengerRecordRepository()
        self.redis_repository = RedisPassengerRecordRepository(self.redis_client, self.in_memory_repository)
        self.redis_registry = RedisCommandRegistry(self.redis_repository)

    def tearDown(self) -> None:
        self.redis_registry.unregister(CommandTest)

    def test_register_destination(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"

        self.redis_registry.register(test_command_handler, test_destination_contact)

        self.assertEqual(test_command_handler, self.redis_registry.get_command_destination(CommandTest))
        self.assertEqual(test_destination_contact, self.redis_registry.get_command_destination_contact(CommandTest))

    def test_unregister(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        self.redis_registry.register(test_command_handler, test_destination_contact)

        self.redis_registry.unregister(CommandTest)

        self.assertIsNone(self.redis_registry.get_command_destination(CommandTest))

    def test_get_registered_passengers(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        self.redis_registry.register(test_command_handler, test_destination_contact)

        registered_passengers = list(self.redis_registry.get_commands_registered())

        expected_commands_registered = [(CommandTest, test_command_handler, test_destination_contact)]
        self.assertCountEqual(expected_commands_registered, registered_passengers)
