from logging import Logger
from unittest import TestCase
from unittest.mock import Mock, call, patch

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.implementations.timing_event_middleware import TimingEventMiddleware


class TestTimingEventMiddleware(TestCase):
    def setUp(self) -> None:
        self.logger_mock = Mock(spec=Logger)
        self.timing_event_middleware = TimingEventMiddleware(self.logger_mock)

    @patch("bus_station.event_terminal.middleware.implementations.timing_event_middleware.time")
    def test_before_consume(self, time_mock):
        test_event = Mock(spec=Event)
        test_event_consumer = Mock(spec=EventConsumer)

        self.timing_event_middleware.before_consume(test_event, test_event_consumer)

        time_mock.time.assert_called_once_with()

    @patch("bus_station.event_terminal.middleware.implementations.timing_event_middleware.time")
    def test_after_consume_without_exception(self, time_mock):
        test_event = Mock(spec=Event)
        test_event_consumer = Mock(spec=EventConsumer)
        time_mock.time.side_effect = [1, 2]

        self.timing_event_middleware.before_consume(test_event, test_event_consumer)
        self.timing_event_middleware.after_consume(test_event, test_event_consumer)

        time_mock.time.assert_has_calls([call(), call()])
        self.logger_mock.info.assert_called_once_with(
            f"Event {test_event} consumed successfully by {test_event_consumer.bus_stop_name()} in 1 seconds"
        )

    @patch("bus_station.event_terminal.middleware.implementations.timing_event_middleware.time")
    def test_after_consume_with_exception(self, time_mock):
        test_event = Mock(spec=Event)
        test_event_consumer = Mock(spec=EventConsumer)
        time_mock.time.side_effect = [1, 2]

        self.timing_event_middleware.before_consume(test_event, test_event_consumer)
        self.timing_event_middleware.after_consume(test_event, test_event_consumer, consume_exception=Exception("Test"))

        time_mock.time.assert_has_calls([call(), call()])
        self.logger_mock.info.assert_called_once_with(
            f"Event {test_event} consumed wrongly by {test_event_consumer.bus_stop_name()} in 1 seconds"
        )
