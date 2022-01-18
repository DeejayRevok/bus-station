from dataclasses import dataclass
from logging import getLogger
from unittest import TestCase

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware_executor import CommandMiddlewareExecutor
from bus_station.command_terminal.middleware.implementations.logging_command_middleware import LoggingCommandMiddleware


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = 0

    def handle(self, command: CommandTest) -> None:
        self.call_count = self.call_count + 1


class TestLoggingCommandMiddleware(TestCase):
    def setUp(self) -> None:
        self.logger = getLogger()
        self.command_middleware_executor = CommandMiddlewareExecutor()
        self.command_middleware_executor.add_middleware_definition(LoggingCommandMiddleware, self.logger, lazy=False)

    def test_execute_with_middleware_logs(self):
        test_command = CommandTest()
        test_command_handler = CommandTestHandler()

        with self.assertLogs(level="INFO") as logs:
            self.command_middleware_executor.execute(test_command, test_command_handler)

            self.assertIn(
                f"Starting handling command {test_command} with {test_command_handler.__class__.__name__}",
                logs.output[0],
            )
            self.assertIn(
                f"Finished handling command {test_command} with {test_command_handler.__class__.__name__}",
                logs.output[1],
            )
        self.assertEqual(1, test_command_handler.call_count)
