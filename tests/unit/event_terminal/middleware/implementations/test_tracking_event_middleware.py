from unittest import TestCase
from unittest.mock import Mock

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.implementations.tracking_event_middleware import TrackingEventMiddleware
from bus_station.tracking_terminal.trackers.passenger_tracker import PassengerTracker


class TestTrackingEventMiddleware(TestCase):
    def setUp(self) -> None:
        self.passenger_tracker_mock = Mock(spec=PassengerTracker)
        self.tracking_event_middleware = TrackingEventMiddleware(self.passenger_tracker_mock)

    def test_before_consume(self):
        test_event = Mock(spec=Event)
        test_event_handler = Mock(spec=EventConsumer)

        self.tracking_event_middleware.before_consume(test_event, test_event_handler)

        self.passenger_tracker_mock.start_tracking.assert_called_once_with(test_event, test_event_handler)

    def test_after_consume_without_exception(self):
        test_event = Mock(spec=Event)
        test_event_handler = Mock(spec=EventConsumer)

        self.tracking_event_middleware.after_consume(test_event, test_event_handler)

        self.passenger_tracker_mock.end_tracking.assert_called_once_with(test_event, test_event_handler, True)

    def test_after_consume_with_exception(self):
        test_event = Mock(spec=Event)
        test_event_handler = Mock(spec=EventConsumer)

        self.tracking_event_middleware.after_consume(
            test_event, test_event_handler, consume_exception=Exception("Test")
        )

        self.passenger_tracker_mock.end_tracking.assert_called_once_with(test_event, test_event_handler, False)
