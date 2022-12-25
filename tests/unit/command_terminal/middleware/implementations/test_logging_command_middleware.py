from logging import Logger
from unittest import TestCase
from unittest.mock import Mock

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.implementations.logging_command_middleware import LoggingCommandMiddleware


class TestLoggingCommandMiddleware(TestCase):
    def setUp(self) -> None:
        self.logger_mock = Mock(spec=Logger)
        self.logging_command_middleware = LoggingCommandMiddleware(self.logger_mock)

    def test_before_handle(self):
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)

        self.logging_command_middleware.before_handle(test_command, test_command_handler)

        self.logger_mock.info.assert_called_once_with(
            f"Starting handling command {test_command} with {test_command_handler.bus_stop_name()}"
        )

    def test_after_handle_without_exception(self):
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)

        self.logging_command_middleware.after_handle(test_command, test_command_handler)

        self.logger_mock.info.assert_called_once_with(
            f"Finished handling command {test_command} with {test_command_handler.bus_stop_name()}"
        )
        self.logger_mock.exception.assert_not_called()

    def test_after_handle_with_exception(self):
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)
        test_exception = Exception("Test exception")

        self.logging_command_middleware.after_handle(
            test_command, test_command_handler, handling_exception=test_exception
        )

        self.logger_mock.info.assert_called_once_with(
            f"Finished handling command {test_command} with {test_command_handler.bus_stop_name()}"
        )
        self.logger_mock.exception.assert_called_once_with(
            test_exception, exc_info=(test_exception.__class__, test_exception, test_exception.__traceback__)
        )
