from dataclasses import dataclass

from redis import Redis

from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.registry.redis_query_registry import RedisQueryRegistry
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class QueryTest(Query):
    pass


class QueryTestHandler(QueryHandler):
    def handle(self, query: QueryTest) -> None:
        pass


class TestRedisQueryRegistry(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)

    def setUp(self) -> None:
        self.redis_repository = RedisPassengerRecordRepository(self.redis_client)
        self.fqn_getter = FQNGetter()
        self.query_handler_resolver = InMemoryBusStopResolver[QueryHandler](fqn_getter=self.fqn_getter)
        self.passenger_class_resolver = PassengerClassResolver()
        self.redis_registry = RedisQueryRegistry(
            redis_repository=self.redis_repository,
            query_handler_resolver=self.query_handler_resolver,
            fqn_getter=self.fqn_getter,
            passenger_class_resolver=self.passenger_class_resolver,
        )

    def tearDown(self) -> None:
        self.redis_registry.unregister(QueryTest)

    def test_register_destination(self):
        test_query_handler = QueryTestHandler()
        test_destination_contact = "test_destination_contact"
        self.query_handler_resolver.add_bus_stop(test_query_handler)

        self.redis_registry.register(test_query_handler, test_destination_contact)

        self.assertEqual(test_query_handler, self.redis_registry.get_query_destination(QueryTest))
        self.assertEqual(test_destination_contact, self.redis_registry.get_query_destination_contact(QueryTest))

    def test_unregister(self):
        test_query_handler = QueryTestHandler()
        test_destination_contact = "test_destination_contact"
        self.redis_registry.register(test_query_handler, test_destination_contact)
        self.query_handler_resolver.add_bus_stop(test_query_handler)

        self.redis_registry.unregister(QueryTest)

        self.assertIsNone(self.redis_registry.get_query_destination(QueryTest))

    def test_get_queries_registered(self):
        test_query_handler = QueryTestHandler()
        test_destination_contact = "test_destination_contact"
        self.redis_registry.register(test_query_handler, test_destination_contact)
        self.query_handler_resolver.add_bus_stop(test_query_handler)

        registered_passengers = self.redis_registry.get_queries_registered()

        expected_querys_registered = {QueryTest}
        self.assertCountEqual(expected_querys_registered, registered_passengers)