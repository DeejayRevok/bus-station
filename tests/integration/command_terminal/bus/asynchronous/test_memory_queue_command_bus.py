import os
import signal
from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Process, Value
from time import sleep

from bus_station.command_terminal.bus.asynchronous.memory_queue_command_bus import MemoryQueueCommandBus
from bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine import MemoryQueueCommandBusEngine
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.command_terminal.middleware.command_middleware_receiver import CommandMiddlewareReceiver
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.shared_terminal.engine.runner.process_engine_runner import ProcessEngineRunner
from bus_station.shared_terminal.engine.runner.self_process_engine_runner import SelfProcessEngineRunner
from bus_station.shared_terminal.factories.memory_queue_factory import memory_queue_factory
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
    @classmethod
    def setUpClass(cls) -> None:
        cls.passenger_serializer = PassengerJSONSerializer()
        cls.passenger_deserializer = PassengerJSONDeserializer()
        cls.command_receiver = CommandMiddlewareReceiver()

    def setUp(self) -> None:
        self.__exhaust_queue()
        self.command_handler_registry = CommandHandlerRegistry()
        self.test_command_handler = CommandTestHandler()
        self.command_handler_registry.register(self.test_command_handler)
        self.memory_queue_bus_engine = MemoryQueueCommandBusEngine(
            self.command_handler_registry,
            self.command_receiver,
            self.passenger_deserializer,
            self.test_command_handler.bus_stop_name(),
        )
        self.memory_queue_command_bus = MemoryQueueCommandBus(self.passenger_serializer)

    def __exhaust_queue(self):
        queue = memory_queue_factory.queue_with_id(CommandTest.passenger_name())
        while not queue.empty():
            queue.get()

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
