from dataclasses import dataclass

from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.query_terminal.bus.synchronous.sync_query_bus import SyncQueryBus
from bus_station.query_terminal.middleware.query_middleware_receiver import QueryMiddlewareReceiver
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.in_memory_query_registry import InMemoryQueryRegistry
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.distributed import clear_context_distributed_id, create_distributed_id
from bus_station.shared_terminal.fqn_getter import FQNGetter
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class QueryTest(Query):
    test_value: str


class QueryTestHandler(QueryHandler):
    def __init__(self):
        self.call_count = 0
        self.distributed_id = ""

    def handle(self, query: QueryTest) -> QueryResponse:
        self.call_count += 1
        self.distributed_id = query.distributed_id
        return QueryResponse(data=query.test_value)


class TestSyncQueryBus(IntegrationTestCase):
    def setUp(self) -> None:
        self.in_memory_repository = InMemoryPassengerRecordRepository()
        self.fqn_getter = FQNGetter()
        self.query_handler_resolver = InMemoryBusStopResolver[QueryHandler](fqn_getter=self.fqn_getter)
        self.passenger_class_resolver = PassengerClassResolver()
        self.in_memory_registry = InMemoryQueryRegistry(
            in_memory_repository=self.in_memory_repository,
            query_handler_resolver=self.query_handler_resolver,
            fqn_getter=self.fqn_getter,
            passenger_class_resolver=self.passenger_class_resolver,
        )
        self.query_middleware_receiver = QueryMiddlewareReceiver()
        self.sync_query_bus = SyncQueryBus(self.in_memory_registry, self.query_middleware_receiver)
        self.distributed_id = create_distributed_id()

    def tearDown(self) -> None:
        clear_context_distributed_id()

    def test_transport_success(self):
        test_query_value = "test_query_value"
        test_query = QueryTest(test_value=test_query_value)
        test_query_handler = QueryTestHandler()
        self.in_memory_registry.register(test_query_handler, test_query_handler)
        self.query_handler_resolver.add_bus_stop(test_query_handler)

        test_query_response = self.sync_query_bus.transport(test_query)

        self.assertEqual(1, test_query_handler.call_count)
        self.assertEqual(test_query_value, test_query_response.data)
        self.assertEqual(self.distributed_id, test_query.distributed_id)
        self.assertEqual(self.distributed_id, test_query_handler.distributed_id)
