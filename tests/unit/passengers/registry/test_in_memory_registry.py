from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.command import Command
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry


class TestInMemoryRegistry(TestCase):
    @patch("builtins.dict")
    def setUp(self, dict_mock) -> None:
        self.dict_mock = dict_mock
        self.in_memory_registry = InMemoryRegistry()

    def test_register(self):
        test_command = Mock(spec=Command)
        test_destination = "test_destination"

        self.in_memory_registry.register_destination(test_command.__class__, test_destination)

        self.dict_mock().__setitem__.assert_called_once_with(test_command.__class__, test_destination)

    def test_get_passenger_destination(self):
        test_command = Mock(spec=Command)
        test_destination = "test_destination"
        self.dict_mock().get.return_value = test_destination

        destination = self.in_memory_registry.get_passenger_destination(test_command.__class__)

        self.assertEqual(test_destination, destination)
        self.dict_mock().get.assert_called_once_with(test_command.__class__)

    def test_unregister(self):
        test_command = Mock(spec=Command)

        self.in_memory_registry.unregister(test_command.__class__)

        self.dict_mock().__delitem__.assert_called_once_with(test_command.__class__)
