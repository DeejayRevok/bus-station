from unittest import TestCase
from unittest.mock import Mock, call

from redis.client import Redis

from bus_station.bus_stop.registration.address.redis_bus_stop_address_registry import RedisBusStopAddressRegistry
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler


class QueryTest(Query):
    pass


class QueryHandlerTest(QueryHandler):
    def handle(self, query: QueryTest) -> None:
        pass


class TestRedisBusStopAddressRegistry(TestCase):
    def setUp(self):
        self.redis_client = Mock(spec=Redis)
        self.registry = RedisBusStopAddressRegistry(self.redis_client)

    def test_register(self):
        self.registry.register(QueryHandlerTest, QueryTest, "address")

        self.redis_client.set.assert_has_calls(
            [
                call(QueryTest.passenger_name(), QueryHandlerTest.bus_stop_name()),
                call(QueryHandlerTest.bus_stop_name(), "address"),
            ]
        )

    def test_get_address_for_bus_stop_passenger_class(self):
        query_handler_name = QueryHandlerTest.bus_stop_name()
        self.redis_client.get.side_effect = [query_handler_name, b"address"]

        address = self.registry.get_address_for_bus_stop_passenger_class(QueryTest)

        self.redis_client.get.assert_has_calls(
            [
                call(QueryTest.passenger_name()),
                call(query_handler_name),
            ]
        )
        self.assertEqual("address", address)

    def test_unregister(self):
        self.registry.unregister(QueryHandlerTest, QueryTest)

        self.redis_client.delete.assert_has_calls(
            [
                call(QueryTest.passenger_name()),
                call(QueryHandlerTest.bus_stop_name()),
            ]
        )
