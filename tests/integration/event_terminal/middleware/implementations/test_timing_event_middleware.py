from dataclasses import dataclass
from logging import getLogger

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware_receiver import EventMiddlewareReceiver
from bus_station.event_terminal.middleware.implementations.timing_event_middleware import TimingEventMiddleware
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class EventTest(Event):
    pass


class EventTestConsumer(EventConsumer):
    def __init__(self):
        self.call_count = 0

    def consume(self, event: EventTest) -> None:
        self.call_count += 1


class TestTimingEventMiddleware(IntegrationTestCase):
    def setUp(self) -> None:
        self.logger = getLogger()
        self.event_middleware_receiver = EventMiddlewareReceiver()
        self.event_middleware_receiver.add_middleware_definition(TimingEventMiddleware, self.logger, lazy=True)

    def test_transport_with_middleware_logs_timing(self):
        test_event = EventTest()
        test_event_consumer = EventTestConsumer()

        with self.assertLogs(level="INFO") as logs:
            self.event_middleware_receiver.receive(test_event, test_event_consumer)

            self.assertIn(
                f"Event {test_event} consumed successfully by {test_event_consumer.__class__.__name__} in",
                logs.output[0],
            )
        self.assertEqual(1, test_event_consumer.call_count)
