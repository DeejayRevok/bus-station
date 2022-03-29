from dataclasses import dataclass
from unittest import TestCase

from bus_station.command_terminal.command import Command
from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class TestPassengerClassResolver(TestCase):
    def setUp(self) -> None:
        self.fqn_getter = FQNGetter()
        self.passenger_class_resolver = PassengerClassResolver()

    def test_resolve_from_fqn_success(self):
        command_fqn = self.fqn_getter.get(CommandTest)

        resolved_passenger_class = self.passenger_class_resolver.resolve_from_fqn(command_fqn)

        self.assertEqual(CommandTest, resolved_passenger_class)
