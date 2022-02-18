from dataclasses import dataclass
from time import sleep

from bus_station.command_terminal.bus.asynchronous.threaded_command_bus import ThreadedCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
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


class TestThreadedCommandBus(IntegrationTestCase):
    def setUp(self) -> None:
        self.in_memory_registry = InMemoryCommandRegistry()
        self.threaded_command_bus = ThreadedCommandBus(self.in_memory_registry)

    def test_execute_success(self):
        test_command = CommandTest()
        test_command_handler = CommandTestHandler()
        self.in_memory_registry.register_destination(test_command_handler, test_command_handler)

        self.threaded_command_bus.execute(test_command)

        sleep(1)
        self.assertEqual(1, test_command_handler.call_count)
