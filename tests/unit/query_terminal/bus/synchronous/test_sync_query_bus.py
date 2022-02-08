from typing import Callable
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry
from bus_station.query_terminal.bus.synchronous.sync_query_bus import SyncQueryBus
from bus_station.query_terminal.handler_for_query_already_registered import HandlerForQueryAlreadyRegistered
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.middleware.query_middleware_executor import QueryMiddlewareExecutor
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse


class TestSyncQueryBus(TestCase):
    def setUp(self) -> None:
        self.query_registry_mock = Mock(spec=InMemoryRegistry)
        self.sync_query_bus = SyncQueryBus(self.query_registry_mock)

    @patch("bus_station.query_terminal.bus.query_bus.get_type_hints")
    def test_register_already_registered(self, get_type_hints_mock):
        test_query_handler = Mock(spec=QueryHandler)
        test_query = Mock(spec=Query)
        get_type_hints_mock.return_value = {"query": test_query.__class__}
        self.query_registry_mock.__contains__ = Mock(spec=Callable)
        self.query_registry_mock.__contains__.return_value = True

        with self.assertRaises(HandlerForQueryAlreadyRegistered) as hfqar:
            self.sync_query_bus.register(test_query_handler)

        self.assertEqual(test_query.__class__.__name__, hfqar.exception.query_name)
        self.query_registry_mock.__contains__.assert_called_once_with(test_query.__class__)

    @patch("bus_station.query_terminal.bus.query_bus.get_type_hints")
    def test_register_success(self, get_type_hints_mock):
        test_query_handler = Mock(spec=QueryHandler)
        test_query = Mock(spec=Query)
        get_type_hints_mock.return_value = {"query": test_query.__class__}
        self.query_registry_mock.__contains__ = Mock(spec=Callable)
        self.query_registry_mock.__contains__.return_value = False

        self.sync_query_bus.register(test_query_handler)

        self.query_registry_mock.__contains__.assert_called_once_with(test_query.__class__)
        self.query_registry_mock.register.assert_called_once_with(test_query.__class__, test_query_handler)

    def test_execute_not_registered(self):
        test_query = Mock(spec=Query)
        self.query_registry_mock.get_passenger_destination.return_value = None

        with self.assertRaises(HandlerNotFoundForQuery) as hnffq:
            self.sync_query_bus.execute(test_query)

        self.assertEqual(test_query.__class__.__name__, hnffq.exception.query_name)
        self.query_registry_mock.get_passenger_destination.assert_called_once_with(test_query.__class__)

    @patch("bus_station.query_terminal.bus.query_bus.get_type_hints")
    @patch.object(QueryMiddlewareExecutor, "execute")
    def test_execute_success(self, middleware_executor_mock, get_type_hints_mock):
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)
        test_query_response = Mock(spec=QueryResponse)
        middleware_executor_mock.return_value = test_query_response
        get_type_hints_mock.return_value = {"query": test_query.__class__}
        self.query_registry_mock.get_passenger_destination.return_value = test_query_handler

        query_response = self.sync_query_bus.execute(test_query)

        middleware_executor_mock.assert_called_once_with(test_query, test_query_handler)
        self.assertEqual(test_query_response, query_response)
        self.query_registry_mock.get_passenger_destination.assert_called_once_with(test_query.__class__)
