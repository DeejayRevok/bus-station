from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Value
from time import sleep

from redis import Redis

from bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus import JsonRPCCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware_receiver import CommandMiddlewareReceiver
from bus_station.command_terminal.registry.redis_command_registry import RedisCommandRegistry
from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = Value(c_int, 0)

    def handle(self, command: CommandTest) -> None:
        self.call_count.value = self.call_count.value + 1


class TestJsonRPCCommandBus(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)

    def setUp(self) -> None:
        self.redis_repository = RedisPassengerRecordRepository(self.redis_client)
        self.fqn_getter = FQNGetter()
        self.command_handler_resolver = InMemoryBusStopResolver(fqn_getter=self.fqn_getter)
        self.passenger_class_resolver = PassengerClassResolver()
        self.redis_registry = RedisCommandRegistry(
            redis_repository=self.redis_repository,
            command_handler_resolver=self.command_handler_resolver,
            fqn_getter=self.fqn_getter,
            passenger_class_resolver=self.passenger_class_resolver,
        )
        self.command_serializer = PassengerJSONSerializer()
        self.command_deserializer = PassengerJSONDeserializer()
        self.bus_host = "localhost"
        self.bus_port = 1234
        self.command_receiver = CommandMiddlewareReceiver()
        self.json_rpc_command_bus = JsonRPCCommandBus(
            self.bus_host,
            self.bus_port,
            self.command_serializer,
            self.command_deserializer,
            self.redis_registry,
            self.command_receiver
        )

    def tearDown(self) -> None:
        self.redis_registry.unregister(CommandTest)
        self.json_rpc_command_bus.stop()

    def test_transport_success(self):
        test_command = CommandTest()
        test_command_handler = CommandTestHandler()
        self.redis_registry.register(test_command_handler, f"http://{self.bus_host}:{self.bus_port}")
        self.command_handler_resolver.add_bus_stop(test_command_handler)
        self.json_rpc_command_bus.start()
        sleep(2)

        for i in range(10):
            self.json_rpc_command_bus.transport(test_command)

            self.assertEqual(i + 1, test_command_handler.call_count.value)
