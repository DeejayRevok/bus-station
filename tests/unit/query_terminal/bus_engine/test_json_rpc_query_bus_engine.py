from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.query_terminal.bus_engine.json_rpc_query_bus_engine import JsonRPCQueryBusEngine
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.registry.remote_query_registry import RemoteQueryRegistry
from bus_station.shared_terminal.json_rpc_server import JsonRPCServer


class TestJsonRPCQueryBusEngine(TestCase):
    def setUp(self) -> None:
        self.server_mock = Mock(spec=JsonRPCServer)
        self.query_registry_mock = Mock(spec=RemoteQueryRegistry)

    @patch("bus_station.query_terminal.bus_engine.json_rpc_query_bus_engine.resolve_passenger_from_bus_stop")
    def test_init_with_query(self, passenger_resolver_mock):
        query_type_mock = Mock(spec=Query, **{"passenger_name.return_value": "test_query"})
        query_handler_mock = Mock(spec=QueryHandler)
        self.query_registry_mock.get_query_destination.return_value = query_handler_mock
        passenger_resolver_mock.return_value = query_type_mock

        JsonRPCQueryBusEngine(self.server_mock, self.query_registry_mock, "test_query")

        self.query_registry_mock.get_query_destination.assert_called_once_with("test_query")
        self.server_mock.register.assert_called_once_with(query_type_mock, query_handler_mock)

    @patch("bus_station.query_terminal.bus_engine.json_rpc_query_bus_engine.resolve_passenger_from_bus_stop")
    def test_start(self, _):
        engine = JsonRPCQueryBusEngine(self.server_mock, self.query_registry_mock, "test_query")

        engine.start()

        self.server_mock.run.assert_called_once_with()
