from dataclasses import dataclass

from bus_station.event_terminal.bus.synchronous.sync_event_bus import SyncEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class EventTest(Event):
    pass


class EventTestConsumer1(EventConsumer):
    def __init__(self):
        self.call_count = 0

    def consume(self, event: EventTest) -> None:
        self.call_count += 1


class EventTestConsumer2(EventConsumer):
    def __init__(self):
        self.call_count = 2

    def consume(self, event: EventTest) -> None:
        self.call_count -= 1


class TestSyncEventBus(IntegrationTestCase):
    def setUp(self) -> None:
        self.in_memory_registry = InMemoryRegistry()
        self.sync_event_bus = SyncEventBus(self.in_memory_registry)

    def test_publish_success(self):
        test_event = EventTest()
        test_event_consumer1 = EventTestConsumer1()
        test_event_consumer2 = EventTestConsumer2()

        self.sync_event_bus.register(test_event_consumer1)
        self.sync_event_bus.register(test_event_consumer2)
        self.sync_event_bus.publish(test_event)

        self.assertEqual(1, test_event_consumer1.call_count)
        self.assertEqual(1, test_event_consumer2.call_count)
