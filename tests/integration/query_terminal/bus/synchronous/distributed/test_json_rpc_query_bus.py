from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Value
from time import sleep

from redis import Redis

from bus_station.passengers.registry.in_memory_passenger_record_repository import InMemoryPassengerRecordRepository
from bus_station.passengers.registry.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus import JsonRPCQueryBus
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.redis_query_registry import RedisQueryRegistry
from bus_station.query_terminal.serialization.query_response_json_deserializer import QueryResponseJSONDeserializer
from bus_station.query_terminal.serialization.query_response_json_serializer import QueryResponseJSONSerializer
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


class TestJsonRPCQueryBus(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_env_ready = False
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)
        cls.test_env_ready = True

    def setUp(self) -> None:
        if self.test_env_ready is False:
            self.fail("Test environment is not ready")
        self.bus_host = "localhost"
        self.bus_port = 1234
        self.in_memory_repository = InMemoryPassengerRecordRepository()
        self.redis_repository = RedisPassengerRecordRepository(self.redis_client, self.in_memory_repository)
        self.redis_registry = RedisQueryRegistry(self.redis_repository)
        self.query_serializer = PassengerJSONSerializer()
        self.query_deserializer = PassengerJSONDeserializer()
        self.query_response_serializer = QueryResponseJSONSerializer()
        self.query_response_deserializer = QueryResponseJSONDeserializer()
        self.json_rpc_query_bus = JsonRPCQueryBus(
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
        self.json_rpc_query_bus.stop()

    def test_execute_success(self):
        test_value = "test_value"
        test_query = QueryTest(test_value=test_value)
        test_query_handler = QueryTestHandler()
        self.redis_registry.register(test_query_handler, f"http://{self.bus_host}:{self.bus_port}")
        self.json_rpc_query_bus.start()
        sleep(2)

        for i in range(10):
            query_response = self.json_rpc_query_bus.execute(test_query)

            self.assertEqual(i + 1, test_query_handler.call_count.value)
            expected_query_response = QueryResponse(data=test_value)
            self.assertEqual(expected_query_response, query_response)
