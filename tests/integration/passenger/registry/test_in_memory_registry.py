from unittest import TestCase

from bus_station.command_terminal.command import Command
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry


class CommandTest(Command):
    pass


class TestInMemoryRegistry(TestCase):
    def setUp(self) -> None:
        self.in_memory_registry = InMemoryRegistry()

    def test_register(self):
        test_destination = "test_destination"

        self.in_memory_registry.register(CommandTest, test_destination)

        self.assertEqual(test_destination, self.in_memory_registry.get_passenger_destination(CommandTest))

    def test_unregister(self):
        test_destination = "test_destination"
        self.in_memory_registry.register(CommandTest, test_destination)

        self.in_memory_registry.unregister(CommandTest)

        self.assertIsNone(self.in_memory_registry.get_passenger_destination(CommandTest))
