from dataclasses import dataclass
from time import sleep

from bus_station.event_terminal.bus.asynchronous.threaded_event_bus import ThreadedEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.event_consumer_registry import EventConsumerRegistry
from bus_station.event_terminal.middleware.event_middleware_receiver import EventMiddlewareReceiver
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


class TestThreadedEventBus(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.event_receiver = EventMiddlewareReceiver()

    def setUp(self) -> None:
        event_consumer_registry = EventConsumerRegistry()
        self.test_event_consumer1 = EventTestConsumer1()
        self.test_event_consumer2 = EventTestConsumer2()

        event_consumer_registry.register(self.test_event_consumer1)
        event_consumer_registry.register(self.test_event_consumer2)

        self.threaded_event_bus = ThreadedEventBus(event_consumer_registry, self.event_receiver)

    def test_transport_success(self):
        test_event = EventTest()

        self.threaded_event_bus.transport(test_event)

        sleep(1)
        self.assertEqual(1, self.test_event_consumer1.call_count)
        self.assertEqual(1, self.test_event_consumer2.call_count)
