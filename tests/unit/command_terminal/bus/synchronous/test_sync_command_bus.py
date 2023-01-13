from unittest import TestCase
from unittest.mock import Mock

from bus_station.command_terminal.bus.synchronous.sync_command_bus import SyncCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver


class TestSyncCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_registry_mock = Mock(spec=InMemoryCommandRegistry)
        self.command_receiver_mock = Mock(spec=PassengerReceiver[Command, CommandHandler])
        self.sync_command_bus = SyncCommandBus(self.command_registry_mock, self.command_receiver_mock)

    def test_transport_not_registered(self):
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        self.command_registry_mock.get_command_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.sync_command_bus.transport(test_command)

        self.assertEqual("test_command", hnffc.exception.command_name)
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with("test_command")

    def test_transport_success(self):
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        test_command_handler = Mock(spec=CommandHandler)
        self.command_registry_mock.get_command_destination_contact.return_value = test_command_handler

        self.sync_command_bus.transport(test_command)

        self.command_receiver_mock.receive.assert_called_once_with(test_command, test_command_handler)
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with("test_command")
