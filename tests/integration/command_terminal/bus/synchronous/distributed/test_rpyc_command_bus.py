import os
import signal
from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Process, Value
from multiprocessing.sharedctypes import Array
from time import sleep
from uuid import uuid4

from redis import Redis

from bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus import RPyCCommandBus
from bus_station.command_terminal.bus_engine.rpyc_command_bus_engine import RPyCCommandBusEngine
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware_receiver import CommandMiddlewareReceiver
from bus_station.command_terminal.registry.redis_command_registry import RedisCommandRegistry
from bus_station.command_terminal.rpyc_command_server import RPyCCommandServer
from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.distributed import clear_context_distributed_id, create_distributed_id
from bus_station.shared_terminal.engine.runner.process_engine_runner import ProcessEngineRunner
from bus_station.shared_terminal.engine.runner.self_process_engine_runner import SelfProcessEngineRunner
from bus_station.shared_terminal.fqn_getter import FQNGetter
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = Value(c_int, 0)
        self.distributed_id = Array("c", str.encode(str(uuid4())))

    def handle(self, command: CommandTest) -> None:
        self.call_count.value = self.call_count.value + 1
        self.distributed_id.value = str.encode(command.distributed_id)


class TestRPyCCommandBus(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)

    def setUp(self) -> None:
        redis_repository = RedisPassengerRecordRepository(self.redis_client)
        fqn_getter = FQNGetter()
        command_handler_resolver = InMemoryBusStopResolver(fqn_getter=fqn_getter)
        passenger_class_resolver = PassengerClassResolver()
        self.redis_registry = RedisCommandRegistry(
            redis_repository=redis_repository,
            command_handler_resolver=command_handler_resolver,
            fqn_getter=fqn_getter,
            passenger_class_resolver=passenger_class_resolver,
        )
        bus_host = "localhost"
        bus_port = 1234
        self.test_command_handler = CommandTestHandler()
        self.redis_registry.register(self.test_command_handler, f"{bus_host}:{bus_port}")
        command_handler_resolver.add_bus_stop(self.test_command_handler)
        command_serializer = PassengerJSONSerializer()
        command_deserializer = PassengerJSONDeserializer()
        command_receiver = CommandMiddlewareReceiver()
        rpyc_server = RPyCCommandServer(bus_host, bus_port, command_deserializer, command_receiver)
        self.rpyc_command_bus_engine = RPyCCommandBusEngine(
            rpyc_server, self.redis_registry, CommandTest.passenger_name()
        )
        self.rpyc_command_bus = RPyCCommandBus(command_serializer, self.redis_registry)
        self.distributed_id = create_distributed_id()

    def tearDown(self) -> None:
        self.redis_registry.unregister(CommandTest.passenger_name())
        clear_context_distributed_id()

    def test_process_engine_transport_success(self):
        test_command = CommandTest()
        with ProcessEngineRunner(engine=self.rpyc_command_bus_engine, should_interrupt=True):
            sleep(1)
            for i in range(10):
                self.rpyc_command_bus.transport(test_command)

                self.assertEqual(i + 1, self.test_command_handler.call_count.value)
                self.assertEqual(self.distributed_id, test_command.distributed_id)
                self.assertEqual(self.distributed_id, self.test_command_handler.distributed_id.value.decode())

    def test_self_process_engine_transport_success(self):
        test_command = CommandTest()
        engine_runner = SelfProcessEngineRunner(engine=self.rpyc_command_bus_engine)
        runner_process = Process(target=engine_runner.run)
        runner_process.start()
        sleep(1)

        try:
            for i in range(10):
                self.rpyc_command_bus.transport(test_command)

                self.assertEqual(i + 1, self.test_command_handler.call_count.value)
                self.assertEqual(self.distributed_id, test_command.distributed_id)
                self.assertEqual(self.distributed_id, self.test_command_handler.distributed_id.value.decode())
        finally:
            os.kill(runner_process.pid, signal.SIGINT)
