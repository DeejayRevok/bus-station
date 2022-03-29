from dataclasses import dataclass
from unittest import TestCase

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter


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
        self.fqn_getter = FQNGetter()
        self.in_memory_bus_stop_resolver = InMemoryBusStopResolver(self.fqn_getter)

    def test_resolve_from_fqn_success(self):
        test_command_handler = CommandTestHandler()
        self.in_memory_bus_stop_resolver.add_bus_stop(test_command_handler)
        command_handler_fnq = self.fqn_getter.get(test_command_handler)

        resolved_bus_stop = self.in_memory_bus_stop_resolver.resolve_from_fqn(command_handler_fnq)

        self.assertEqual(test_command_handler, resolved_bus_stop)
