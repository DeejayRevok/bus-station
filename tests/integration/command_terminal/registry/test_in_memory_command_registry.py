from dataclasses import dataclass

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.registry.in_memory_passenger_record_repository import InMemoryPassengerRecordRepository
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def handle(self, command: CommandTest) -> None:
        pass


class TestInMemoryCommandRegistry(IntegrationTestCase):
    def setUp(self) -> None:
        self.in_memory_repository = InMemoryPassengerRecordRepository()
        self.in_memory_registry = InMemoryCommandRegistry(self.in_memory_repository)

    def test_register_destination(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"

        self.in_memory_registry.register(test_command_handler, test_destination_contact)

        self.assertEqual(test_command_handler, self.in_memory_registry.get_command_destination(CommandTest))
        self.assertEqual(test_destination_contact, self.in_memory_registry.get_command_destination_contact(CommandTest))

    def test_unregister(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        self.in_memory_registry.register(test_command_handler, test_destination_contact)

        self.in_memory_registry.unregister(CommandTest)

        self.assertIsNone(self.in_memory_registry.get_command_destination(CommandTest))

    def test_get_registered_passengers(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        self.in_memory_registry.register(test_command_handler, test_destination_contact)

        registered_passengers = list(self.in_memory_registry.get_commands_registered())

        expected_commands_registered = [(CommandTest, test_command_handler, test_destination_contact)]
        self.assertCountEqual(expected_commands_registered, registered_passengers)
