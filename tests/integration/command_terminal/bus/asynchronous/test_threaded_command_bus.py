from dataclasses import dataclass
from time import sleep

from bus_station.command_terminal.bus.asynchronous.threaded_command_bus import ThreadedCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.command_terminal.middleware.command_middleware_receiver import CommandMiddlewareReceiver
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = 0

    def handle(self, command: CommandTest) -> None:
        self.call_count += 1


class TestThreadedCommandBus(IntegrationTestCase):
    def setUp(self) -> None:
        self.test_command_handler = CommandTestHandler()
        command_handler_registry = CommandHandlerRegistry()
        command_handler_registry.register(self.test_command_handler)
        command_receiver = CommandMiddlewareReceiver()
        self.threaded_command_bus = ThreadedCommandBus(command_handler_registry, command_receiver)

    def test_transport_success(self):
        test_command = CommandTest()

        self.threaded_command_bus.transport(test_command)

        sleep(1)
        self.assertEqual(1, self.test_command_handler.call_count)
