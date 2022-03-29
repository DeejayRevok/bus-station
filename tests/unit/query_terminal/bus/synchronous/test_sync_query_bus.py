from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.query_terminal.bus.synchronous.sync_query_bus import SyncQueryBus
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.middleware.query_middleware_executor import QueryMiddlewareExecutor
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.in_memory_query_registry import InMemoryQueryRegistry


class TestSyncQueryBus(TestCase):
    def setUp(self) -> None:
        self.query_registry_mock = Mock(spec=InMemoryQueryRegistry)
        self.sync_query_bus = SyncQueryBus(self.query_registry_mock)

    def test_execute_not_registered(self):
        test_query = Mock(spec=Query)
        self.query_registry_mock.get_query_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForQuery) as hnffq:
            self.sync_query_bus.execute(test_query)

        self.assertEqual(test_query.__class__.__name__, hnffq.exception.query_name)
        self.query_registry_mock.get_query_destination_contact.assert_called_once_with(test_query.__class__)

    @patch.object(QueryMiddlewareExecutor, "execute")
    def test_execute_success(self, middleware_executor_mock):
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)
        test_query_response = Mock(spec=QueryResponse)
        middleware_executor_mock.return_value = test_query_response
        self.query_registry_mock.get_query_destination_contact.return_value = test_query_handler

        query_response = self.sync_query_bus.execute(test_query)

        middleware_executor_mock.assert_called_once_with(test_query, test_query_handler)
        self.assertEqual(test_query_response, query_response)
        self.query_registry_mock.get_query_destination_contact.assert_called_once_with(test_query.__class__)
