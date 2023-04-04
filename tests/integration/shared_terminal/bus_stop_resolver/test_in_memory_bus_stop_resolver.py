from dataclasses import dataclass
from unittest import TestCase

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.fqn import resolve_fqn


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = 0

    def handle(self, command: CommandTest) -> None:
        self.call_count += 1


class TestInMemoryBusStopResolver(TestCase):
    def setUp(self) -> None:
        self.in_memory_bus_stop_resolver = InMemoryBusStopResolver()

    def test_resolve_from_fqn_success(self):
        test_command_handler = CommandTestHandler()
        self.in_memory_bus_stop_resolver.add_bus_stop(test_command_handler)
        command_handler_fnq = resolve_fqn(test_command_handler)

        resolved_bus_stop = self.in_memory_bus_stop_resolver.resolve_from_fqn(command_handler_fnq)

        self.assertEqual(test_command_handler, resolved_bus_stop)
