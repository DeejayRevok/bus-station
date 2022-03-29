from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Queue, Value
from time import sleep

from bus_station.event_terminal.bus.asynchronous.process_event_bus import ProcessEventBus
from bus_station.event_terminal.bus.synchronous.sync_event_bus import SyncEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry
from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
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


class TestProcessEventBus(IntegrationTestCase):
    def setUp(self) -> None:
        self.passenger_serializer = PassengerJSONSerializer()
        self.passenger_deserializer = PassengerJSONDeserializer()
        self.in_memory_repository = InMemoryPassengerRecordRepository()
        self.fqn_getter = FQNGetter()
        self.event_consumer_resolver = InMemoryBusStopResolver[EventConsumer](fqn_getter=self.fqn_getter)
        self.passenger_class_resolver = PassengerClassResolver()
        self.in_memory_registry = InMemoryEventRegistry(
            in_memory_repository=self.in_memory_repository,
            event_consumer_resolver=self.event_consumer_resolver,
            fqn_getter=self.fqn_getter,
            passenger_class_resolver=self.passenger_class_resolver,
        )
        self.sync_event_bus = SyncEventBus(self.in_memory_registry)
        self.process_event_bus = ProcessEventBus(
            self.passenger_serializer, self.passenger_deserializer, self.in_memory_registry
        )

    def tearDown(self) -> None:
        self.process_event_bus.stop()

    def test_publish_success(self):
        test_event = EventTest()
        test_event_consumer1 = EventTestConsumer1()
        test_event_consumer2 = EventTestConsumer2()
        test_queue = Queue()
        self.in_memory_registry.register(test_event_consumer1, test_queue)
        self.in_memory_registry.register(test_event_consumer2, test_queue)
        self.event_consumer_resolver.add_bus_stop(test_event_consumer1)
        self.event_consumer_resolver.add_bus_stop(test_event_consumer2)
        self.process_event_bus.start()

        self.process_event_bus.publish(test_event)

        sleep(1)
        self.assertEqual(1, test_event_consumer1.call_count.value)
        self.assertEqual(1, test_event_consumer2.call_count.value)
