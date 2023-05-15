from dataclasses import dataclass

from bus_station.bus_stop.resolvers.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.query_terminal.bus.synchronous.sync_query_bus import SyncQueryBus
from bus_station.query_terminal.middleware.query_middleware_receiver import QueryMiddlewareReceiver
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_handler_registry import QueryHandlerRegistry
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.shared_terminal.fqn import resolve_fqn
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
        query_handler_resolver = InMemoryBusStopResolver[QueryHandler]()
        self.test_query_handler = QueryTestHandler()
        query_handler_registry = QueryHandlerRegistry(
            bus_stop_resolver=query_handler_resolver,
        )
        query_middleware_receiver = QueryMiddlewareReceiver()

        query_handler_resolver.add_bus_stop(self.test_query_handler)
        query_handler_registry.register(resolve_fqn(self.test_query_handler))

        self.sync_query_bus = SyncQueryBus(query_handler_registry, query_middleware_receiver)

    def test_transport_success(self):
        test_query_value = "test_query_value"
        test_query = QueryTest(test_value=test_query_value)

        test_query_response = self.sync_query_bus.transport(test_query)

        self.assertEqual(1, self.test_query_handler.call_count)
        self.assertEqual(test_query_value, test_query_response.data)
