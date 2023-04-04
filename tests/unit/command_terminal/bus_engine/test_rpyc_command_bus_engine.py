from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.bus_engine.rpyc_command_bus_engine import RPyCCommandBusEngine
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.shared_terminal.rpyc_server import RPyCServer


class TestRPyCCommandBusEngine(TestCase):
    def setUp(self) -> None:
        self.rpyc_server_mock = Mock(spec=RPyCServer)
        self.command_registry_mock = Mock(spec=RemoteCommandRegistry)

    @patch("bus_station.command_terminal.bus_engine.rpyc_command_bus_engine.resolve_passenger_class_from_bus_stop")
    def test_init_with_command(self, passenger_resolver_mock):
        command_type_mock = Mock(spec=Command)
        passenger_resolver_mock.return_value = command_type_mock
        command_handler_mock = Mock(spec=CommandHandler)
        self.command_registry_mock.get_command_destination.return_value = command_handler_mock

        RPyCCommandBusEngine(self.rpyc_server_mock, self.command_registry_mock, "test_command")

        self.command_registry_mock.get_command_destination.assert_called_once_with("test_command")
        self.rpyc_server_mock.register.assert_called_once_with(command_type_mock, command_handler_mock)
        passenger_resolver_mock.assert_called_once_with(command_handler_mock, "handle", "command", Command)

    @patch("bus_station.command_terminal.bus_engine.rpyc_command_bus_engine.resolve_passenger_class_from_bus_stop")
    def test_start(self, _):
        engine = RPyCCommandBusEngine(self.rpyc_server_mock, self.command_registry_mock, "test_command")

        engine.start()

        self.rpyc_server_mock.run.assert_called_once_with()
