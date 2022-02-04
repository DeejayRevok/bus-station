from dataclasses import dataclass

from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.bus.synchronous.sync_query_bus import SyncQueryBus
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class QueryTest(Query):
    test_value: str


class QueryTestHandler(QueryHandler):
    def __init__(self):
        self.call_count = 0

    def handle(self, query: QueryTest) -> QueryResponse:
        self.call_count += 1
        return QueryResponse(data=query.test_value)


class TestSyncQueryBus(IntegrationTestCase):
    def setUp(self) -> None:
        self.in_memory_registry = InMemoryRegistry()
        self.sync_query_bus = SyncQueryBus(self.in_memory_registry)

    def test_execute_success(self):
        test_query_value = "test_query_value"
        test_query = QueryTest(test_value=test_query_value)
        test_query_handler = QueryTestHandler()

        self.sync_query_bus.register(test_query_handler)
        test_query_response = self.sync_query_bus.execute(test_query)

        self.assertEqual(1, test_query_handler.call_count)
        self.assertEqual(test_query_value, test_query_response.data)
