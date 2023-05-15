from dataclasses import dataclass

from bus_station.bus_stop.resolvers.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.command_terminal.bus.synchronous.sync_command_bus import SyncCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.command_terminal.middleware.command_middleware_receiver import CommandMiddlewareReceiver
from bus_station.shared_terminal.fqn import resolve_fqn
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = 0

    def handle(self, command: CommandTest) -> None:
        self.call_count += 1


class TestSyncCommandBus(IntegrationTestCase):
    def setUp(self) -> None:
        command_handler_resolver = InMemoryBusStopResolver()
        command_handler_registry = CommandHandlerRegistry(
            bus_stop_resolver=command_handler_resolver,
        )
        self.test_command_handler = CommandTestHandler()
        command_handler_resolver.add_bus_stop(self.test_command_handler)
        command_handler_registry.register(resolve_fqn(self.test_command_handler))
        command_receiver = CommandMiddlewareReceiver()
        self.sync_command_bus = SyncCommandBus(command_handler_registry, command_receiver)

    def test_transport_success(self):
        test_command = CommandTest()

        self.sync_command_bus.transport(test_command)

        self.assertEqual(1, self.test_command_handler.call_count)
