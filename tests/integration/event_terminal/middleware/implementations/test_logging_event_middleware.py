from dataclasses import dataclass
from logging import getLogger

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware_receiver import EventMiddlewareReceiver
from bus_station.event_terminal.middleware.implementations.logging_event_middleware import LoggingEventMiddleware
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class EventTest(Event):
    pass


class EventTestConsumer(EventConsumer):
    def __init__(self):
        self.call_count = 0

    def consume(self, event: EventTest) -> None:
        self.call_count += 1


class TestLoggingEventMiddleware(IntegrationTestCase):
    def setUp(self) -> None:
        self.logger = getLogger()
        self.event_middleware_receiver = EventMiddlewareReceiver()
        self.event_middleware_receiver.add_middleware_definition(LoggingEventMiddleware, self.logger, lazy=False)

    def test_transport_with_middleware_logs(self):
        test_event = EventTest()
        test_event_consumer = EventTestConsumer()

        with self.assertLogs(level="INFO") as logs:
            self.event_middleware_receiver.receive(test_event, test_event_consumer)

            self.assertIn(
                f"Starting consuming event {test_event} with {test_event_consumer.__class__.__name__}", logs.output[0]
            )
            self.assertIn(
                f"Finished consuming event {test_event} with {test_event_consumer.__class__.__name__}", logs.output[1]
            )
        self.assertEqual(1, test_event_consumer.call_count)
