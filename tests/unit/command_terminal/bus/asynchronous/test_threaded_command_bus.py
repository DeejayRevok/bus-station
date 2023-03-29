from threading import Thread
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.bus.asynchronous.threaded_command_bus import ThreadedCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver


class TestThreadedCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_registry_mock = Mock(spec=InMemoryCommandRegistry)
        self.command_receiver_mock = Mock(spec=PassengerReceiver[Command, CommandHandler])
        self.threaded_command_bus = ThreadedCommandBus(self.command_registry_mock, self.command_receiver_mock)

    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    def test_transport_not_registered(self, get_context_root_passenger_id_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        self.command_registry_mock.get_command_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.threaded_command_bus.transport(test_command)

        self.assertEqual(test_command.passenger_name(), hnffc.exception.command_name)
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with("test_command")
        test_command.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")

    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    @patch("bus_station.command_terminal.bus.asynchronous.threaded_command_bus.Thread")
    def test_transport_success(self, thread_mock, get_context_root_passenger_id_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        test_command_handler = Mock(spec=CommandHandler)
        test_thread = Mock(spec=Thread)
        thread_mock.return_value = test_thread
        self.command_registry_mock.get_command_destination_contact.return_value = test_command_handler

        self.threaded_command_bus.transport(test_command)

        thread_mock.assert_called_once_with(
            target=self.command_receiver_mock.receive, args=(test_command, test_command_handler)
        )
        test_thread.start.assert_called_once_with()
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with("test_command")
        test_command.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")
