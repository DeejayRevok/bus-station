import os
import signal
from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Process, Value
from time import sleep

from bus_station.bus_stop.resolvers.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.event_terminal.bus.asynchronous.memory_queue_event_bus import MemoryQueueEventBus
from bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine import MemoryQueueEventBusEngine
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.event_consumer_registry import EventConsumerRegistry
from bus_station.event_terminal.middleware.event_middleware_receiver import EventMiddlewareReceiver
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.shared_terminal.engine.runner.process_engine_runner import ProcessEngineRunner
from bus_station.shared_terminal.engine.runner.self_process_engine_runner import SelfProcessEngineRunner
from bus_station.shared_terminal.fqn import resolve_fqn
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class EventTest(Event):
    pass


class EventTestConsumer1(EventConsumer):
    def __init__(self):
        self.call_count = Value(c_int, 0)

    def consume(self, event: EventTest) -> None:
        self.call_count.value = self.call_count.value + 1


class EventTestConsumer2(EventConsumer):
    def __init__(self):
        self.call_count = Value(c_int, 2)

    def consume(self, event: EventTest) -> None:
        self.call_count.value = self.call_count.value - 1


class TestMemoryQueueEventBus(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.event_serializer = PassengerJSONSerializer()
        cls.event_deserializer = PassengerJSONDeserializer()
        cls.event_consumer_1_fqn = resolve_fqn(EventTestConsumer1)
        cls.event_consumer_2_fqn = resolve_fqn(EventTestConsumer2)
        cls.event_receiver = EventMiddlewareReceiver()

    def setUp(self) -> None:
        event_consumer_resolver = InMemoryBusStopResolver()
        event_consumer_registry = EventConsumerRegistry(bus_stop_resolver=event_consumer_resolver)
        event_middleware_receiver = EventMiddlewareReceiver()
        self.test_event_consumer1 = EventTestConsumer1()
        self.test_event_consumer2 = EventTestConsumer2()

        event_consumer_resolver.add_bus_stop(self.test_event_consumer1)
        event_consumer_resolver.add_bus_stop(self.test_event_consumer2)
        event_consumer_registry.register(self.event_consumer_1_fqn)
        event_consumer_registry.register(self.event_consumer_2_fqn)

        self.memory_queue_event_bus = MemoryQueueEventBus(
            self.event_serializer,
            event_consumer_registry,
        )
        self.memory_queue_event_bus_engine1 = MemoryQueueEventBusEngine(
            event_consumer_registry,
            event_middleware_receiver,
            self.event_deserializer,
            self.test_event_consumer1.bus_stop_name(),
        )
        self.memory_queue_event_bus_engine2 = MemoryQueueEventBusEngine(
            event_consumer_registry,
            event_middleware_receiver,
            self.event_deserializer,
            self.test_event_consumer2.bus_stop_name(),
        )

    def test_process_transport_success(self):
        test_event = EventTest()
        with ProcessEngineRunner(self.memory_queue_event_bus_engine1, should_interrupt=False):
            with ProcessEngineRunner(self.memory_queue_event_bus_engine2, should_interrupt=False):
                for i in range(10):
                    self.memory_queue_event_bus.transport(test_event)

                    sleep(1)
                    self.assertEqual(i + 1, self.test_event_consumer1.call_count.value)
                    self.assertEqual(1 - i, self.test_event_consumer2.call_count.value)

    def test_self_process_transport_success(self):
        test_event = EventTest()
        engine_runner1 = SelfProcessEngineRunner(engine=self.memory_queue_event_bus_engine1)
        runner_process1 = Process(target=engine_runner1.run)
        runner_process1.start()
        engine_runner2 = SelfProcessEngineRunner(engine=self.memory_queue_event_bus_engine2)
        runner_process2 = Process(target=engine_runner2.run)
        runner_process2.start()

        try:
            for i in range(10):
                self.memory_queue_event_bus.transport(test_event)

                sleep(1)
                self.assertEqual(i + 1, self.test_event_consumer1.call_count.value)
                self.assertEqual(1 - i, self.test_event_consumer2.call_count.value)
        finally:
            os.kill(runner_process1.pid, signal.SIGINT)
            os.kill(runner_process2.pid, signal.SIGINT)
