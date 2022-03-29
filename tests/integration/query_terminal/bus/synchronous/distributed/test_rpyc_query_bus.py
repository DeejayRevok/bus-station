from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Value
from time import sleep

from redis import Redis

from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.query_terminal.bus.synchronous.distributed.rpyc_query_bus import RPyCQueryBus
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.redis_query_registry import RedisQueryRegistry
from bus_station.query_terminal.serialization.query_response_json_deserializer import QueryResponseJSONDeserializer
from bus_station.query_terminal.serialization.query_response_json_serializer import QueryResponseJSONSerializer
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class QueryTest(Query):
    test_value: str


class QueryTestHandler(QueryHandler):
    def __init__(self):
        self.call_count = Value(c_int, 0)

    def handle(self, query: QueryTest) -> QueryResponse:
        self.call_count.value = self.call_count.value + 1
        return QueryResponse(data=query.test_value)


class TestRPyCQueryBus(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)

    def setUp(self) -> None:
        self.bus_host = "localhost"
        self.bus_port = 1234
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
        self.query_serializer = PassengerJSONSerializer()
        self.query_deserializer = PassengerJSONDeserializer()
        self.query_response_serializer = QueryResponseJSONSerializer()
        self.query_response_deserializer = QueryResponseJSONDeserializer()
        self.rpyc_query_bus = RPyCQueryBus(
            "localhost",
            self.bus_port,
            self.query_serializer,
            self.query_deserializer,
            self.query_response_serializer,
            self.query_response_deserializer,
            self.redis_registry,
        )

    def tearDown(self) -> None:
        self.redis_registry.unregister(QueryTest)
        self.rpyc_query_bus.stop()

    def test_execute_success(self):
        test_query_value = "test_query_value"
        test_query = QueryTest(test_value=test_query_value)
        test_query_handler = QueryTestHandler()
        self.redis_registry.register(test_query_handler, f"{self.bus_host}:{self.bus_port}")
        self.query_handler_resolver.add_bus_stop(test_query_handler)
        self.rpyc_query_bus.start()
        sleep(2)

        test_query_response = self.rpyc_query_bus.execute(test_query)

        self.assertEqual(1, test_query_handler.call_count.value)
        self.assertEqual(test_query_value, test_query_response.data)
