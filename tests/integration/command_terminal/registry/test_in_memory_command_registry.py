from dataclasses import dataclass

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter
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
        self.fqn_getter = FQNGetter()
        self.command_handler_resolver = InMemoryBusStopResolver(fqn_getter=self.fqn_getter)
        self.passenger_class_resolver = PassengerClassResolver()
        self.in_memory_registry = InMemoryCommandRegistry(
            in_memory_repository=self.in_memory_repository,
            command_handler_resolver=self.command_handler_resolver,
            fqn_getter=self.fqn_getter,
            passenger_class_resolver=self.passenger_class_resolver,
        )

    def test_register(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        self.command_handler_resolver.add_bus_stop(test_command_handler)

        self.in_memory_registry.register(test_command_handler, test_destination_contact)

        self.assertEqual(test_command_handler, self.in_memory_registry.get_command_destination(CommandTest))
        self.assertEqual(test_destination_contact, self.in_memory_registry.get_command_destination_contact(CommandTest))

    def test_unregister(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        self.in_memory_registry.register(test_command_handler, test_destination_contact)
        self.command_handler_resolver.add_bus_stop(test_command_handler)

        self.in_memory_registry.unregister(CommandTest)

        self.assertIsNone(self.in_memory_registry.get_command_destination(CommandTest))

    def test_get_commands_registered(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        self.in_memory_registry.register(test_command_handler, test_destination_contact)

        registered_passengers = self.in_memory_registry.get_commands_registered()

        expected_commands_registered = {CommandTest}
        self.assertCountEqual(expected_commands_registered, registered_passengers)
