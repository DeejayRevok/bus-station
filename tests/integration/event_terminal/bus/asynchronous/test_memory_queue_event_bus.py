import os
import signal
from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Process, Queue, Value
from time import sleep

from bus_station.event_terminal.bus.asynchronous.memory_queue_event_bus import MemoryQueueEventBus
from bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine import MemoryQueueEventBusEngine
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware_receiver import EventMiddlewareReceiver
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry
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
    def setUp(self) -> None:
        passenger_serializer = PassengerJSONSerializer()
        passenger_deserializer = PassengerJSONDeserializer()
        in_memory_repository = InMemoryPassengerRecordRepository()
        fqn_getter = FQNGetter()
        event_consumer_resolver = InMemoryBusStopResolver(fqn_getter=fqn_getter)
        passenger_class_resolver = PassengerClassResolver()
        in_memory_registry = InMemoryEventRegistry(
            in_memory_repository=in_memory_repository,
            event_consumer_resolver=event_consumer_resolver,
            fqn_getter=fqn_getter,
            passenger_class_resolver=passenger_class_resolver,
        )
        self.event_queue1 = Queue()
        self.event_queue2 = Queue()
        event_middleware_receiver = EventMiddlewareReceiver()
        self.test_event_consumer1 = EventTestConsumer1()
        self.test_event_consumer2 = EventTestConsumer2()
        in_memory_registry.register(self.test_event_consumer1, self.event_queue1)
        in_memory_registry.register(self.test_event_consumer2, self.event_queue2)
        event_consumer_resolver.add_bus_stop(self.test_event_consumer1)
        event_consumer_resolver.add_bus_stop(self.test_event_consumer2)

        self.memory_queue_event_bus = MemoryQueueEventBus(
            passenger_serializer,
            in_memory_registry,
        )
        self.memory_queue_event_bus_engine1 = MemoryQueueEventBusEngine(
            in_memory_registry, event_middleware_receiver, passenger_deserializer, EventTest, self.test_event_consumer1
        )
        self.memory_queue_event_bus_engine2 = MemoryQueueEventBusEngine(
            in_memory_registry, event_middleware_receiver, passenger_deserializer, EventTest, self.test_event_consumer2
        )

    def tearDown(self) -> None:
        self.event_queue1.close()
        self.event_queue2.close()

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
