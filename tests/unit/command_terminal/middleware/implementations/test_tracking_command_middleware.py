from unittest import TestCase
from unittest.mock import Mock

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.implementations.tracking_command_middleware import (
    TrackingCommandMiddleware,
)
from bus_station.tracking_terminal.trackers.passenger_tracker import PassengerTracker


class TestTrackingCommandMiddleware(TestCase):
    def setUp(self) -> None:
        self.passenger_tracker_mock = Mock(spec=PassengerTracker)
        self.tracking_command_middleware = TrackingCommandMiddleware(self.passenger_tracker_mock)

    def test_before_handle(self):
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)

        self.tracking_command_middleware.before_handle(test_command, test_command_handler)

        self.passenger_tracker_mock.start_tracking.assert_called_once_with(test_command, test_command_handler)

    def test_after_handle_without_exception(self):
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)

        self.tracking_command_middleware.after_handle(test_command, test_command_handler)

        self.passenger_tracker_mock.end_tracking.assert_called_once_with(test_command, test_command_handler, True)

    def test_after_handle_with_exception(self):
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)
        test_exception = Exception("Test exception")

        self.tracking_command_middleware.after_handle(
            test_command, test_command_handler, handling_exception=test_exception
        )

        self.passenger_tracker_mock.end_tracking.assert_called_once_with(test_command, test_command_handler, False)
