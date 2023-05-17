from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.bus.synchronous.sync_command_bus import SyncCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver


class TestSyncCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_handler_registry_mock = Mock(spec=CommandHandlerRegistry)
        self.command_receiver_mock = Mock(spec=PassengerReceiver[Command, CommandHandler])
        self.sync_command_bus = SyncCommandBus(self.command_handler_registry_mock, self.command_receiver_mock)

    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    def test_transport_not_registered(self, get_context_root_passenger_id_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        self.command_handler_registry_mock.get_handler_from_command.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.sync_command_bus.transport(test_command)

        self.assertEqual("test_command", hnffc.exception.command_name)
        self.command_handler_registry_mock.get_handler_from_command.assert_called_once_with("test_command")
        test_command.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")

    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    def test_transport_success(self, get_context_root_passenger_id_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        test_command_handler = Mock(spec=CommandHandler)
        self.command_handler_registry_mock.get_handler_from_command.return_value = test_command_handler

        self.sync_command_bus.transport(test_command)

        self.command_receiver_mock.receive.assert_called_once_with(test_command, test_command_handler)
        self.command_handler_registry_mock.get_handler_from_command.assert_called_once_with("test_command")
        test_command.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")
