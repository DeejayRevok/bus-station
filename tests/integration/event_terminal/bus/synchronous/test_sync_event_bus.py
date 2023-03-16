from dataclasses import dataclass

from bus_station.event_terminal.bus.synchronous.sync_event_bus import SyncEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware_receiver import EventMiddlewareReceiver
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry
from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.distributed import clear_context_distributed_id, create_distributed_id
from bus_station.shared_terminal.fqn_getter import FQNGetter
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class EventTest(Event):
    pass


class EventTestConsumer1(EventConsumer):
    def __init__(self):
        self.call_count = 0
        self.distributed_id = ""

    def consume(self, event: EventTest) -> None:
        self.call_count += 1
        self.distributed_id = event.distributed_id


class EventTestConsumer2(EventConsumer):
    def __init__(self):
        self.call_count = 2
        self.distributed_id = ""

    def consume(self, event: EventTest) -> None:
        self.call_count -= 1
        self.distributed_id = event.distributed_id


class TestSyncEventBus(IntegrationTestCase):
    def setUp(self) -> None:
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
        self.event_middleware_receiver = EventMiddlewareReceiver()
        self.sync_event_bus = SyncEventBus(self.in_memory_registry, self.event_middleware_receiver)
        self.distributed_id = create_distributed_id()

    def tearDown(self) -> None:
        clear_context_distributed_id()

    def test_transport_success(self):
        test_event = EventTest()
        test_event_consumer1 = EventTestConsumer1()
        test_event_consumer2 = EventTestConsumer2()
        self.in_memory_registry.register(test_event_consumer1, test_event_consumer1)
        self.in_memory_registry.register(test_event_consumer2, test_event_consumer2)
        self.event_consumer_resolver.add_bus_stop(test_event_consumer1)
        self.event_consumer_resolver.add_bus_stop(test_event_consumer2)

        self.sync_event_bus.transport(test_event)

        self.assertEqual(1, test_event_consumer1.call_count)
        self.assertEqual(1, test_event_consumer2.call_count)
        self.assertEqual(self.distributed_id, test_event.distributed_id)
        self.assertEqual(self.distributed_id, test_event_consumer1.distributed_id)
        self.assertEqual(self.distributed_id, test_event_consumer2.distributed_id)
