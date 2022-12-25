from unittest import TestCase
from unittest.mock import Mock, call

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

    def test_init_with_command_handler_found(self):
        command_type_mock = Mock(spec=Command)
        command_handler_mock = Mock(spec=CommandHandler)
        self.command_registry_mock.get_command_destination.return_value = command_handler_mock

        JsonRPCCommandBusEngine(self.server_mock, self.command_registry_mock, command_type_mock.__class__)

        self.command_registry_mock.get_command_destination.assert_called_once_with(command_type_mock.__class__)
        self.server_mock.register.assert_called_once_with(command_type_mock.__class__, command_handler_mock)

    def test_init_with_command_handler_not_found(self):
        command_type_mock = Mock(spec=Command)
        self.command_registry_mock.get_command_destination.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            JsonRPCCommandBusEngine(self.server_mock, self.command_registry_mock, command_type_mock.__class__)

        self.assertEqual("command.bus_station.command_terminal.command.Command", hnffc.exception.command_name)
        self.command_registry_mock.get_command_destination.assert_called_once_with(command_type_mock.__class__)
        self.server_mock.register.assert_not_called()

    def test_init_without_command(self):
        command_type_mock = Mock(spec=Command)
        command_handler_mock = Mock(spec=CommandHandler)
        self.command_registry_mock.get_commands_registered.return_value = [
            command_type_mock.__class__,
            command_type_mock.__class__,
        ]
        self.command_registry_mock.get_command_destination.return_value = command_handler_mock

        JsonRPCCommandBusEngine(self.server_mock, self.command_registry_mock)

        self.command_registry_mock.get_command_destination.assert_has_calls(
            [call(command_type_mock.__class__), call(command_type_mock.__class__)]
        )
        self.server_mock.register.assert_has_calls(
            [
                call(command_type_mock.__class__, command_handler_mock),
                call(command_type_mock.__class__, command_handler_mock),
            ]
        )
        self.command_registry_mock.get_commands_registered.assert_called_once_with()

    def test_start(self):
        self.command_registry_mock.get_commands_registered.return_value = []
        engine = JsonRPCCommandBusEngine(self.server_mock, self.command_registry_mock)

        engine.start()

        self.server_mock.run.assert_called_once_with()
