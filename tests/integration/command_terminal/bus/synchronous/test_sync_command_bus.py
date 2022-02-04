from dataclasses import dataclass

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.bus.synchronous.sync_command_bus import SyncCommandBus
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry
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
        self.in_memory_registry = InMemoryRegistry()
        self.sync_command_bus = SyncCommandBus(self.in_memory_registry)

    def test_execute_success(self):
        test_command = CommandTest()
        test_command_handler = CommandTestHandler()

        self.sync_command_bus.register(test_command_handler)
        self.sync_command_bus.execute(test_command)

        self.assertEqual(1, test_command_handler.call_count)
