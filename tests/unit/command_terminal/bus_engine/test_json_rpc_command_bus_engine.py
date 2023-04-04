from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.bus_engine.json_rpc_command_bus_engine import JsonRPCCommandBusEngine
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.shared_terminal.json_rpc_server import JsonRPCServer


class TestJsonRPCCommandBusEngine(TestCase):
    def setUp(self) -> None:
        self.server_mock = Mock(spec=JsonRPCServer)
        self.command_registry_mock = Mock(spec=RemoteCommandRegistry)

    @patch("bus_station.command_terminal.bus_engine.json_rpc_command_bus_engine.resolve_passenger_class_from_bus_stop")
    def test_init_with_command_handler_found(self, passenger_resolver_mock):
        command_name = "test_command"
        command_type_mock = Mock(spec=Command)
        passenger_resolver_mock.return_value = command_type_mock
        command_handler_mock = Mock(spec=CommandHandler)
        self.command_registry_mock.get_command_destination.return_value = command_handler_mock

        JsonRPCCommandBusEngine(self.server_mock, self.command_registry_mock, command_name)

        self.command_registry_mock.get_command_destination.assert_called_once_with(command_name)
        self.server_mock.register.assert_called_once_with(command_type_mock, command_handler_mock)
        passenger_resolver_mock.assert_called_once_with(command_handler_mock, "handle", "command", Command)

    def test_init_with_command_handler_not_found(self):
        command_name = "test_command"
        self.command_registry_mock.get_command_destination.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            JsonRPCCommandBusEngine(self.server_mock, self.command_registry_mock, command_name)

        self.assertEqual(command_name, hnffc.exception.command_name)
        self.command_registry_mock.get_command_destination.assert_called_once_with(command_name)
        self.server_mock.register.assert_not_called()

    @patch("bus_station.command_terminal.bus_engine.json_rpc_command_bus_engine.resolve_passenger_class_from_bus_stop")
    def test_start(self, _):
        engine = JsonRPCCommandBusEngine(self.server_mock, self.command_registry_mock, "test_command")

        engine.start()

        self.server_mock.run.assert_called_once_with()
