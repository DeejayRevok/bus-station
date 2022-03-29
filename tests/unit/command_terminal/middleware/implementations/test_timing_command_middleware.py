from logging import Logger
from unittest import TestCase
from unittest.mock import Mock, call, patch

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.implementations.timing_command_middleware import TimingCommandMiddleware


class TestTimingCommandMiddleware(TestCase):
    def setUp(self) -> None:
        self.logger_mock = Mock(spec=Logger)
        self.timing_command_middleware = TimingCommandMiddleware(self.logger_mock)

    @patch("bus_station.command_terminal.middleware.implementations.timing_command_middleware.time")
    def test_before_handle(self, time_mock):
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)

        self.timing_command_middleware.before_handle(test_command, test_command_handler)

        time_mock.time.assert_called_once_with()

    @patch("bus_station.command_terminal.middleware.implementations.timing_command_middleware.time")
    def test_after_handle(self, time_mock):
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)
        time_mock.time.side_effect = [1, 2]

        self.timing_command_middleware.before_handle(test_command, test_command_handler)
        self.timing_command_middleware.after_handle(test_command, test_command_handler)

        time_mock.time.assert_has_calls([call(), call()])
        self.logger_mock.info.assert_called_once_with(
            f"Command {test_command} handled by {test_command_handler.__class__.__name__} in 1 seconds"
        )
