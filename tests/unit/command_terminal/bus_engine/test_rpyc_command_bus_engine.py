from unittest import TestCase
from unittest.mock import Mock, call

from bus_station.command_terminal.bus_engine.rpyc_command_bus_engine import RPyCCommandBusEngine
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.shared_terminal.rpyc_server import RPyCServer


class TestRPyCCommandBusEngine(TestCase):
    def setUp(self) -> None:
        self.rpyc_server_mock = Mock(spec=RPyCServer)
        self.command_registry_mock = Mock(spec=RemoteCommandRegistry)

    def test_init_with_command(self):
        command_type_mock = Mock(spec=Command)
        command_handler_mock = Mock(spec=CommandHandler)
        self.command_registry_mock.get_command_destination.return_value = command_handler_mock

        RPyCCommandBusEngine(self.rpyc_server_mock, self.command_registry_mock, command_type_mock.__class__)

        self.command_registry_mock.get_command_destination.assert_called_once_with(command_type_mock.__class__)
        self.rpyc_server_mock.register.assert_called_once_with(command_type_mock.__class__, command_handler_mock)

    def test_init_without_command(self):
        command_type_mock = Mock(spec=Command)
        command_handler_mock = Mock(spec=CommandHandler)
        self.command_registry_mock.get_commands_registered.return_value = [
            command_type_mock.__class__,
            command_type_mock.__class__,
        ]
        self.command_registry_mock.get_command_destination.return_value = command_handler_mock

        RPyCCommandBusEngine(self.rpyc_server_mock, self.command_registry_mock)

        self.command_registry_mock.get_command_destination.assert_has_calls(
            [call(command_type_mock.__class__), call(command_type_mock.__class__)]
        )
        self.rpyc_server_mock.register.assert_has_calls(
            [
                call(command_type_mock.__class__, command_handler_mock),
                call(command_type_mock.__class__, command_handler_mock),
            ]
        )
        self.command_registry_mock.get_commands_registered.assert_called_once_with()

    def test_start(self):
        self.command_registry_mock.get_commands_registered.return_value = []
        engine = RPyCCommandBusEngine(self.rpyc_server_mock, self.command_registry_mock)

        engine.start()

        self.rpyc_server_mock.run.assert_called_once_with()
