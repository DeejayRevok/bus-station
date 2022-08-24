from unittest import TestCase
from unittest.mock import Mock, call

from bus_station.query_terminal.bus_engine.rpyc_query_bus_engine import RPyCQueryBusEngine
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.registry.remote_query_registry import RemoteQueryRegistry
from bus_station.shared_terminal.rpyc_server import RPyCServer


class TestRPyCQueryBusEngine(TestCase):
    def setUp(self) -> None:
        self.rpyc_server_mock = Mock(spec=RPyCServer)
        self.query_registry_mock = Mock(spec=RemoteQueryRegistry)

    def test_init_with_query(self):
        query_type_mock = Mock(spec=Query)
        query_handler_mock = Mock(spec=QueryHandler)
        self.query_registry_mock.get_query_destination.return_value = query_handler_mock

        RPyCQueryBusEngine(self.rpyc_server_mock, self.query_registry_mock, query_type_mock.__class__)

        self.query_registry_mock.get_query_destination.assert_called_once_with(query_type_mock.__class__)
        self.rpyc_server_mock.register.assert_called_once_with(query_type_mock.__class__, query_handler_mock)

    def test_init_without_query(self):
        query_type_mock = Mock(spec=Query)
        query_handler_mock = Mock(spec=QueryHandler)
        self.query_registry_mock.get_queries_registered.return_value = [
            query_type_mock.__class__,
            query_type_mock.__class__,
        ]
        self.query_registry_mock.get_query_destination.return_value = query_handler_mock

        RPyCQueryBusEngine(self.rpyc_server_mock, self.query_registry_mock)

        self.query_registry_mock.get_query_destination.assert_has_calls(
            [call(query_type_mock.__class__), call(query_type_mock.__class__)]
        )
        self.rpyc_server_mock.register.assert_has_calls(
            [call(query_type_mock.__class__, query_handler_mock), call(query_type_mock.__class__, query_handler_mock)]
        )
        self.query_registry_mock.get_queries_registered.assert_called_once_with()

    def test_start(self):
        self.query_registry_mock.get_queries_registered.return_value = []
        engine = RPyCQueryBusEngine(self.rpyc_server_mock, self.query_registry_mock)

        engine.start()

        self.rpyc_server_mock.run.assert_called_once_with()
