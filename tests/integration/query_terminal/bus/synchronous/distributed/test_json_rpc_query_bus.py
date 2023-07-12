import os
import signal
from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Process, Value
from time import sleep

from redis import Redis

from bus_station.bus_stop.registration.address.redis_bus_stop_address_registry import RedisBusStopAddressRegistry
from bus_station.bus_stop.resolvers.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus import JsonRPCQueryBus
from bus_station.query_terminal.bus_engine.json_rpc_query_bus_engine import JsonRPCQueryBusEngine
from bus_station.query_terminal.json_rpc_query_server import JsonRPCQueryServer
from bus_station.query_terminal.middleware.query_middleware_receiver import QueryMiddlewareReceiver
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_handler_registry import QueryHandlerRegistry
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.serialization.query_response_json_deserializer import QueryResponseJSONDeserializer
from bus_station.query_terminal.serialization.query_response_json_serializer import QueryResponseJSONSerializer
from bus_station.shared_terminal.engine.runner.process_engine_runner import ProcessEngineRunner
from bus_station.shared_terminal.engine.runner.self_process_engine_runner import SelfProcessEngineRunner
from bus_station.shared_terminal.fqn import resolve_fqn
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
        redis_host = cls.redis["host"]
        redis_port = cls.redis["port"]
        cls.query_handler_fqn = resolve_fqn(QueryTestHandler)
        cls.bus_host = "localhost"
        cls.bus_port = 1234

        redis_client = Redis(host=redis_host, port=redis_port)
        cls.redis_address_registry = RedisBusStopAddressRegistry(redis_client)
        cls.redis_address_registry.register(QueryTestHandler, f"http://{cls.bus_host}:{cls.bus_port}")

        cls.query_handler_resolver = InMemoryBusStopResolver()
        cls.query_serializer = PassengerJSONSerializer()
        cls.query_deserializer = PassengerJSONDeserializer()
        cls.query_receiver = QueryMiddlewareReceiver()
        cls.query_response_serializer = QueryResponseJSONSerializer()
        cls.query_response_deserializer = QueryResponseJSONDeserializer()
        cls.json_rpc_server = JsonRPCQueryServer(
            cls.bus_host, cls.bus_port, cls.query_deserializer, cls.query_receiver, cls.query_response_serializer
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.redis_address_registry.unregister(QueryTestHandler)

    def setUp(self) -> None:
        self.query_handler_registry = QueryHandlerRegistry(
            bus_stop_resolver=self.query_handler_resolver,
        )
        self.test_query_handler = QueryTestHandler()
        self.query_handler_resolver.add_bus_stop(self.test_query_handler)
        self.query_handler_registry.register(self.query_handler_fqn)

        self.json_rpc_query_bus_engine = JsonRPCQueryBusEngine(
            server=self.json_rpc_server,
            query_handler_registry=self.query_handler_registry,
            query_handler_name=self.test_query_handler.bus_stop_name(),
        )
        self.json_rpc_query_bus = JsonRPCQueryBus(
            self.query_serializer, self.query_response_deserializer, self.redis_address_registry
        )

    def tearDown(self) -> None:
        self.query_handler_registry.unregister(self.query_handler_fqn)

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
