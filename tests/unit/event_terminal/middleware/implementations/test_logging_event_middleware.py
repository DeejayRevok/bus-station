from logging import Logger
from unittest import TestCase
from unittest.mock import Mock

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.implementations.logging_event_middleware import LoggingEventMiddleware


class TestLoggingEventMiddleware(TestCase):
    def setUp(self) -> None:
        self.logger_mock = Mock(spec=Logger)
        self.logging_event_middleware = LoggingEventMiddleware(self.logger_mock)

    def test_before_consume(self):
        test_event = Mock(spec=Event)
        test_event_consumer = Mock(spec=EventConsumer)

        self.logging_event_middleware.before_consume(test_event, test_event_consumer)

        self.logger_mock.info.assert_called_once_with(
            f"Starting consuming event {test_event} with {test_event_consumer.bus_stop_name()}"
        )

    def test_after_consume_without_exception(self):
        test_event = Mock(spec=Event)
        test_event_consumer = Mock(spec=EventConsumer)

        self.logging_event_middleware.after_consume(test_event, test_event_consumer)

        self.logger_mock.info.assert_called_once_with(
            f"Finished consuming event {test_event} with {test_event_consumer.bus_stop_name()}"
        )
        self.logger_mock.exception.assert_not_called()

    def test_after_consume_with_exception(self):
        test_event = Mock(spec=Event)
        test_event_consumer = Mock(spec=EventConsumer)
        test_exception = Exception("Test exception")

        self.logging_event_middleware.after_consume(test_event, test_event_consumer, consume_exception=test_exception)

        self.logger_mock.info.assert_called_once_with(
            f"Finished consuming event {test_event} with {test_event_consumer.bus_stop_name()}"
        )
        self.logger_mock.exception.assert_called_once_with(
            test_exception, exc_info=(test_exception.__class__, test_exception, test_exception.__traceback__)
        )
