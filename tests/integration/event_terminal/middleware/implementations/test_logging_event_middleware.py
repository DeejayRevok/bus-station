from dataclasses import dataclass
from logging import getLogger
from unittest import TestCase

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware_executor import EventMiddlewareExecutor
from bus_station.event_terminal.middleware.implementations.logging_event_middleware import LoggingEventMiddleware


@dataclass(frozen=True)
class EventTest(Event):
    pass


class EventTestConsumer(EventConsumer):
    def __init__(self):
        self.call_count = 0

    def consume(self, event: EventTest) -> None:
        self.call_count += 1


class TestLoggingEventMiddleware(TestCase):
    def setUp(self) -> None:
        self.logger = getLogger()
        self.event_middleware_executor = EventMiddlewareExecutor()
        self.event_middleware_executor.add_middleware_definition(LoggingEventMiddleware, self.logger, lazy=False)

    def test_publish_with_middleware_logs(self):
        test_event = EventTest()
        test_event_consumer = EventTestConsumer()

        with self.assertLogs(level="INFO") as logs:
            self.event_middleware_executor.execute(test_event, test_event_consumer)

            self.assertIn(
                f"Starting consuming event {test_event} with {test_event_consumer.__class__.__name__}", logs.output[0]
            )
            self.assertIn(
                f"Finished consuming event {test_event} with {test_event_consumer.__class__.__name__}", logs.output[1]
            )
        self.assertEqual(1, test_event_consumer.call_count)
