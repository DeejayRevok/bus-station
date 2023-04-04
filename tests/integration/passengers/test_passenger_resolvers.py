from dataclasses import dataclass
from unittest import TestCase

from bus_station.command_terminal.command import Command
from bus_station.passengers.passenger_resolvers import resolve_passenger_class_from_fqn
from bus_station.shared_terminal.fqn import resolve_fqn


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class TestPassengerResolvers(TestCase):
    def test_resolve_passenger_class_from_fqn(self):
        command_fqn = resolve_fqn(CommandTest)

        resolved_passenger_class = resolve_passenger_class_from_fqn(command_fqn)

        self.assertEqual(CommandTest, resolved_passenger_class)
