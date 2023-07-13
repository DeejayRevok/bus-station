from unittest import TestCase
from unittest.mock import Mock

from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.query_terminal.bus_engine.rpyc_query_bus_engine import RPyCQueryBusEngine
from bus_station.query_terminal.query_handler_not_found import QueryHandlerNotFound
from bus_station.shared_terminal.rpyc_server import RPyCServer


class TestRPyCQueryBusEngine(TestCase):
    def setUp(self):
        self.server = Mock(spec=RPyCServer)
        self.registry = Mock(spec=CommandHandlerRegistry)

    def test_initialize_registers_command_handler_in_server(self):
        handler = Mock()
        handler_name = "handler_name"
        self.registry.get_bus_stop_by_name.return_value = handler
        test_command_mock = Mock()
        handler.passenger.return_value = test_command_mock

        RPyCQueryBusEngine(self.server, self.registry, handler_name)

        self.registry.get_bus_stop_by_name.assert_called_once_with(handler_name)
        self.server.register.assert_called_once_with(test_command_mock, handler)

    def test_initialize_raises_exception_if_command_handler_not_found(self):
        handler_name = "handler_name"
        self.registry.get_bus_stop_by_name.return_value = None

        with self.assertRaises(QueryHandlerNotFound) as context:
            RPyCQueryBusEngine(self.server, self.registry, handler_name)

        self.assertEqual(handler_name, context.exception.query_handler_name)
        self.registry.get_bus_stop_by_name.assert_called_once_with(handler_name)

    def test_start_runs_the_server(self):
        handler_name = "handler_name"
        engine = RPyCQueryBusEngine(self.server, self.registry, handler_name)

        engine.start()

        self.server.run.assert_called_once()
