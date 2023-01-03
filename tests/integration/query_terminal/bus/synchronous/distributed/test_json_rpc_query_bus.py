import os
import signal
from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Process, Value
from time import sleep

from redis import Redis

from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus import JsonRPCQueryBus
from bus_station.query_terminal.bus_engine.json_rpc_query_bus_engine import JsonRPCQueryBusEngine
from bus_station.query_terminal.json_rpc_query_server import JsonRPCQueryServer
from bus_station.query_terminal.middleware.query_middleware_receiver import QueryMiddlewareReceiver
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.redis_query_registry import RedisQueryRegistry
from bus_station.query_terminal.serialization.query_response_json_deserializer import QueryResponseJSONDeserializer
from bus_station.query_terminal.serialization.query_response_json_serializer import QueryResponseJSONSerializer
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.engine.runner.process_engine_runner import ProcessEngineRunner
from bus_station.shared_terminal.engine.runner.self_process_engine_runner import SelfProcessEngineRunner
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


class TestJsonRPCQueryBus(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)

    def setUp(self) -> None:
        bus_host = "localhost"
        bus_port = 1234
        redis_repository = RedisPassengerRecordRepository(self.redis_client)
        fqn_getter = FQNGetter()
        query_handler_resolver = InMemoryBusStopResolver[QueryHandler](fqn_getter=fqn_getter)
        passenger_class_resolver = PassengerClassResolver()
        self.redis_registry = RedisQueryRegistry(
            redis_repository=redis_repository,
            query_handler_resolver=query_handler_resolver,
            fqn_getter=fqn_getter,
            passenger_class_resolver=passenger_class_resolver,
        )
        query_serializer = PassengerJSONSerializer()
        query_deserializer = PassengerJSONDeserializer()
        query_response_serializer = QueryResponseJSONSerializer()
        query_response_deserializer = QueryResponseJSONDeserializer()
        query_middleware_receiver = QueryMiddlewareReceiver()
        json_rpc_server = JsonRPCQueryServer(
            bus_host, bus_port, query_deserializer, query_middleware_receiver, query_response_serializer
        )
        self.test_query_handler = QueryTestHandler()
        self.redis_registry.register(self.test_query_handler, f"http://{bus_host}:{bus_port}")
        query_handler_resolver.add_bus_stop(self.test_query_handler)
        self.json_rpc_query_bus_engine = JsonRPCQueryBusEngine(
            server=json_rpc_server,
            query_registry=self.redis_registry,
        )
        self.json_rpc_query_bus = JsonRPCQueryBus(
            query_serializer,
            query_response_deserializer,
            self.redis_registry,
        )

    def tearDown(self) -> None:
        self.redis_registry.unregister(QueryTest)

    def test_process_engine_transport_success(self):
        test_value = "test_value"
        test_query = QueryTest(test_value=test_value)

        with ProcessEngineRunner(engine=self.json_rpc_query_bus_engine, should_interrupt=True):
            sleep(2)

            for i in range(10):
                query_response = self.json_rpc_query_bus.transport(test_query)

                self.assertEqual(i + 1, self.test_query_handler.call_count.value)
                expected_query_response = QueryResponse(data=test_value)
                self.assertEqual(expected_query_response, query_response)

    def test_self_process_engine_transport_success(self):
        test_value = "test_value"
        test_query = QueryTest(test_value=test_value)
        engine_runner = SelfProcessEngineRunner(engine=self.json_rpc_query_bus_engine)
        runner_process = Process(target=engine_runner.run)
        runner_process.start()
        sleep(1)

        try:
            for i in range(10):
                query_response = self.json_rpc_query_bus.transport(test_query)

                self.assertEqual(i + 1, self.test_query_handler.call_count.value)
                expected_query_response = QueryResponse(data=test_value)
                self.assertEqual(expected_query_response, query_response)
        finally:
            os.kill(runner_process.pid, signal.SIGINT)
