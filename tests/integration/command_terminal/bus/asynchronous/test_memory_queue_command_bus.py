import os
import signal
from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Process, Queue, Value
from time import sleep

from bus_station.command_terminal.bus.asynchronous.memory_queue_command_bus import MemoryQueueCommandBus
from bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine import MemoryQueueCommandBusEngine
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware_receiver import CommandMiddlewareReceiver
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
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

    def handle(self, command: CommandTest) -> None:
        self.call_count.value = self.call_count.value + 1


class TestMemoryQueueCommandBus(IntegrationTestCase):
    def setUp(self) -> None:
        passenger_serializer = PassengerJSONSerializer()
        passenger_deserializer = PassengerJSONDeserializer()
        in_memory_repository = InMemoryPassengerRecordRepository()
        fqn_getter = FQNGetter()
        command_handler_resolver = InMemoryBusStopResolver(fqn_getter=fqn_getter)
        passenger_class_resolver = PassengerClassResolver()
        in_memory_registry = InMemoryCommandRegistry(
            in_memory_repository=in_memory_repository,
            command_handler_resolver=command_handler_resolver,
            fqn_getter=fqn_getter,
            passenger_class_resolver=passenger_class_resolver,
        )
        self.command_queue = Queue()
        command_receiver = CommandMiddlewareReceiver()
        self.test_command_handler = CommandTestHandler()
        in_memory_registry.register(self.test_command_handler, self.command_queue)
        command_handler_resolver.add_bus_stop(self.test_command_handler)
        self.memory_queue_bus_engine = MemoryQueueCommandBusEngine(
            in_memory_registry, command_receiver, passenger_deserializer, CommandTest
        )
        self.memory_queue_command_bus = MemoryQueueCommandBus(passenger_serializer, in_memory_registry)

    def tearDown(self) -> None:
        self.command_queue.close()

    def test_process_transport_success(self):
        test_command = CommandTest()
        with ProcessEngineRunner(self.memory_queue_bus_engine, should_interrupt=False):
            self.memory_queue_command_bus.transport(test_command)

            sleep(1)
            self.assertEqual(1, self.test_command_handler.call_count.value)

    def test_self_process_transport_success(self):
        test_command = CommandTest()
        engine_runner = SelfProcessEngineRunner(engine=self.memory_queue_bus_engine)
        runner_process = Process(target=engine_runner.run)
        runner_process.start()

        try:
            for i in range(10):
                self.memory_queue_command_bus.transport(test_command)

                sleep(1)
                self.assertEqual(i + 1, self.test_command_handler.call_count.value)
        finally:
            os.kill(runner_process.pid, signal.SIGINT)
