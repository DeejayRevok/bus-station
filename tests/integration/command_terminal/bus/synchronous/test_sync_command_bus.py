from dataclasses import dataclass

from bus_station.command_terminal.bus.synchronous.sync_command_bus import SyncCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware_receiver import CommandMiddlewareReceiver
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
    def __init__(self):
        self.call_count = 0

    def handle(self, command: CommandTest) -> None:
        self.call_count += 1


class TestSyncCommandBus(IntegrationTestCase):
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
        self.command_receiver = CommandMiddlewareReceiver()
        self.sync_command_bus = SyncCommandBus(self.in_memory_registry, self.command_receiver)

    def test_transport_success(self):
        test_command = CommandTest()
        test_command_handler = CommandTestHandler()
        self.in_memory_registry.register(test_command_handler, test_command_handler)
        self.command_handler_resolver.add_bus_stop(test_command_handler)

        self.sync_command_bus.transport(test_command)

        self.assertEqual(1, test_command_handler.call_count)
