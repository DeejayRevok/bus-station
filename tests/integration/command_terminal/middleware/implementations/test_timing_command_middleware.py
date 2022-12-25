from dataclasses import dataclass
from logging import getLogger

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware_receiver import CommandMiddlewareReceiver
from bus_station.command_terminal.middleware.implementations.timing_command_middleware import TimingCommandMiddleware
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = 0

    def handle(self, command: CommandTest) -> None:
        self.call_count = self.call_count + 1


class TestTimingCommandMiddleware(IntegrationTestCase):
    def setUp(self) -> None:
        self.logger = getLogger()
        self.command_middleware_receiver = CommandMiddlewareReceiver()
        self.command_middleware_receiver.add_middleware_definition(TimingCommandMiddleware, self.logger, lazy=True)

    def test_receive_with_middleware_logs_timing(self):
        test_command = CommandTest()
        test_command_handler = CommandTestHandler()

        with self.assertLogs(level="INFO") as logs:
            self.command_middleware_receiver.receive(test_command, test_command_handler)

            self.assertIn(
                f"Command {test_command} handled successfully by {test_command_handler.bus_stop_name()} in",
                logs.output[0],
            )
        self.assertEqual(1, test_command_handler.call_count)
