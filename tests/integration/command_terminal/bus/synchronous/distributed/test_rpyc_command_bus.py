import os
import signal
from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Process, Value
from time import sleep

from redis import Redis

from bus_station.bus_stop.registration.address.redis_bus_stop_address_registry import RedisBusStopAddressRegistry
from bus_station.bus_stop.resolvers.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus import RPyCCommandBus
from bus_station.command_terminal.bus_engine.rpyc_command_bus_engine import RPyCCommandBusEngine
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.command_terminal.middleware.command_middleware_receiver import CommandMiddlewareReceiver
from bus_station.command_terminal.rpyc_command_server import RPyCCommandServer
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.shared_terminal.engine.runner.process_engine_runner import ProcessEngineRunner
from bus_station.shared_terminal.engine.runner.self_process_engine_runner import SelfProcessEngineRunner
from bus_station.shared_terminal.fqn import resolve_fqn
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = Value(c_int, 0)

    def handle(self, command: CommandTest) -> None:
        self.call_count.value = self.call_count.value + 1


class TestRPyCCommandBus(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        redis_host = cls.redis["host"]
        redis_port = cls.redis["port"]
        cls.command_handler_fqn = resolve_fqn(CommandTestHandler)
        cls.bus_host = "localhost"
        cls.bus_port = 1234

        redis_client = Redis(host=redis_host, port=redis_port)
        cls.redis_address_registry = RedisBusStopAddressRegistry(redis_client)
        cls.redis_address_registry.register(CommandTestHandler, f"{cls.bus_host}:{cls.bus_port}")

        cls.command_handler_resolver = InMemoryBusStopResolver()
        cls.command_serializer = PassengerJSONSerializer()
        cls.command_deserializer = PassengerJSONDeserializer()
        cls.command_receiver = CommandMiddlewareReceiver()
        cls.rpyc_server = RPyCCommandServer(cls.bus_host, cls.bus_port, cls.command_deserializer, cls.command_receiver)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.redis_address_registry.unregister(CommandTestHandler)

    def setUp(self) -> None:
        self.command_handler_registry = CommandHandlerRegistry(
            bus_stop_resolver=self.command_handler_resolver,
        )
        self.test_command_handler = CommandTestHandler()
        self.command_handler_resolver.add_bus_stop(self.test_command_handler)
        self.command_handler_registry.register(self.command_handler_fqn)

        self.rpyc_command_bus_engine = RPyCCommandBusEngine(
            rpyc_server=self.rpyc_server,
            command_handler_registry=self.command_handler_registry,
            command_handler_name=self.test_command_handler.bus_stop_name(),
        )
        self.rpyc_command_bus = RPyCCommandBus(self.command_serializer, self.redis_address_registry)

    def tearDown(self) -> None:
        self.command_handler_registry.unregister(self.command_handler_fqn)

    def test_process_engine_transport_success(self):
        test_command = CommandTest()
        with ProcessEngineRunner(engine=self.rpyc_command_bus_engine, should_interrupt=True):
            sleep(1)
            for i in range(10):
                self.rpyc_command_bus.transport(test_command)

                self.assertEqual(i + 1, self.test_command_handler.call_count.value)

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
        finally:
            os.kill(runner_process.pid, signal.SIGINT)
