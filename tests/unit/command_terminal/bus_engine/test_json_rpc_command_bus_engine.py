from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.bus_engine.json_rpc_command_bus_engine import JsonRPCCommandBusEngine
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_not_found import CommandHandlerNotFound
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.command_terminal.json_rpc_command_server import JsonRPCCommandServer


class TestJsonRPCCommandBusEngine(TestCase):
    def setUp(self):
        self.server = Mock(spec=JsonRPCCommandServer)
        self.registry = Mock(spec=CommandHandlerRegistry)

    @patch("bus_station.command_terminal.bus_engine.json_rpc_command_bus_engine.resolve_passenger_class_from_bus_stop")
    def test_initialize_registers_command_handler_in_server(self, passenger_resolver_mock):
        handler = Mock(spec=CommandHandler)
        handler_name = "handler_name"
        self.registry.get_bus_stop_by_name.return_value = handler
        test_command_mock = Mock()
        passenger_resolver_mock.return_value = test_command_mock

        JsonRPCCommandBusEngine(self.server, self.registry, handler_name)

        self.registry.get_bus_stop_by_name.assert_called_once_with(handler_name)
        self.server.register.assert_called_once_with(test_command_mock, handler)

    @patch("bus_station.command_terminal.bus_engine.json_rpc_command_bus_engine.resolve_passenger_class_from_bus_stop")
    def test_initialize_raises_exception_if_command_handler_not_found(self, _):
        handler_name = "handler_name"
        self.registry.get_bus_stop_by_name.return_value = None

        with self.assertRaises(CommandHandlerNotFound) as context:
            JsonRPCCommandBusEngine(self.server, self.registry, handler_name)

        self.assertEqual(handler_name, context.exception.command_handler_name)
        self.registry.get_bus_stop_by_name.assert_called_once_with(handler_name)

    @patch("bus_station.command_terminal.bus_engine.json_rpc_command_bus_engine.resolve_passenger_class_from_bus_stop")
    def test_start_runs_the_server(self, _):
        handler_name = "handler_name"
        engine = JsonRPCCommandBusEngine(self.server, self.registry, handler_name)
        engine.start()

        self.server.run.assert_called_once()
