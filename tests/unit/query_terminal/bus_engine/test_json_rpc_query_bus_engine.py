from unittest import TestCase
from unittest.mock import Mock

from bus_station.query_terminal.bus_engine.json_rpc_query_bus_engine import JsonRPCQueryBusEngine
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_handler_registry import QueryHandlerRegistry
from bus_station.shared_terminal.json_rpc_server import JsonRPCServer


class TestJsonRPCQueryBusEngine(TestCase):
    def setUp(self) -> None:
        self.server = Mock(spec=JsonRPCServer)
        self.registry = Mock(spec=QueryHandlerRegistry)

    def test_initialize_registers_query_handler_in_server(self):
        handler = Mock(spec=QueryHandler)
        handler_name = "handler_name"
        self.registry.get_bus_stop_by_name.return_value = handler
        test_query_mock = Mock()
        handler.passenger.return_value = test_query_mock

        JsonRPCQueryBusEngine(self.server, self.registry, handler_name)

        self.registry.get_bus_stop_by_name.assert_called_once_with(handler_name)
        self.server.register.assert_called_once_with(test_query_mock, handler)

    def test_start(self):
        engine = JsonRPCQueryBusEngine(self.server, self.registry, "test_query")

        engine.start()

        self.server.run.assert_called_once_with()
