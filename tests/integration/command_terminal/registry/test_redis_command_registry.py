from dataclasses import dataclass

from redis import Redis

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.redis_command_registry import RedisCommandRegistry
from bus_station.passengers.passenger_record.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
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
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)

    def setUp(self) -> None:
        self.redis_repository = RedisPassengerRecordRepository(self.redis_client)
        self.command_handler_resolver = InMemoryBusStopResolver()
        self.redis_registry = RedisCommandRegistry(
            redis_repository=self.redis_repository,
            command_handler_resolver=self.command_handler_resolver,
        )

    def tearDown(self) -> None:
        self.redis_registry.unregister(CommandTest.passenger_name())

    def test_register(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        self.command_handler_resolver.add_bus_stop(test_command_handler)

        self.redis_registry.register(test_command_handler, test_destination_contact)

        self.assertEqual(
            test_command_handler, self.redis_registry.get_command_destination(CommandTest.passenger_name())
        )
        self.assertEqual(
            test_destination_contact, self.redis_registry.get_command_destination_contact(CommandTest.passenger_name())
        )

    def test_unregister(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        self.redis_registry.register(test_command_handler, test_destination_contact)
        self.command_handler_resolver.add_bus_stop(test_command_handler)

        self.redis_registry.unregister(CommandTest.passenger_name())

        self.assertIsNone(self.redis_registry.get_command_destination(CommandTest.passenger_name()))

    def test_get_commands_registered(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        self.redis_registry.register(test_command_handler, test_destination_contact)
        self.command_handler_resolver.add_bus_stop(test_command_handler)

        registered_passengers = self.redis_registry.get_commands_registered()

        expected_commands_registered = {CommandTest}
        self.assertCountEqual(expected_commands_registered, registered_passengers)
