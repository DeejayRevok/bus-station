from dataclasses import dataclass

from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.registry.in_memory_query_registry import InMemoryQueryRegistry
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class QueryTest(Query):
    pass


class QueryTestHandler(QueryHandler):
    def handle(self, query: QueryTest) -> None:
        pass


class TestInMemoryQueryRegistry(IntegrationTestCase):
    def setUp(self) -> None:
        self.in_memory_repository = InMemoryPassengerRecordRepository()
        self.query_handler_resolver = InMemoryBusStopResolver[QueryHandler]()
        self.in_memory_registry = InMemoryQueryRegistry(
            in_memory_repository=self.in_memory_repository,
            query_handler_resolver=self.query_handler_resolver,
        )

    def test_register(self):
        test_query_handler = QueryTestHandler()
        test_destination_contact = "test_destination_contact"
        self.query_handler_resolver.add_bus_stop(test_query_handler)

        self.in_memory_registry.register(test_query_handler, test_destination_contact)

        self.assertEqual(test_query_handler, self.in_memory_registry.get_query_destination(QueryTest.passenger_name()))
        self.assertEqual(
            test_destination_contact, self.in_memory_registry.get_query_destination_contact(QueryTest.passenger_name())
        )

    def test_unregister(self):
        test_query_handler = QueryTestHandler()
        test_destination_contact = "test_destination_contact"
        self.in_memory_registry.register(test_query_handler, test_destination_contact)
        self.query_handler_resolver.add_bus_stop(test_query_handler)

        self.in_memory_registry.unregister(QueryTest.passenger_name())

        self.assertIsNone(self.in_memory_registry.get_query_destination(QueryTest.passenger_name()))

    def test_get_queries_registered(self):
        test_query_handler = QueryTestHandler()
        test_destination_contact = "test_destination_contact"
        self.in_memory_registry.register(test_query_handler, test_destination_contact)
        self.query_handler_resolver.add_bus_stop(test_query_handler)

        registered_passengers = self.in_memory_registry.get_queries_registered()

        expected_querys_registered = {QueryTest}
        self.assertCountEqual(expected_querys_registered, registered_passengers)
