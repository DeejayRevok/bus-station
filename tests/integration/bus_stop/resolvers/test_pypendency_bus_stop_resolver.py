from dataclasses import dataclass

from pypendency.argument import Argument
from pypendency.container import Container
from pypendency.definition import Definition

from bus_station.bus_stop.resolvers.pypendency_bus_stop_resolver import PypendencyBusStopResolver
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.shared_terminal.fqn import resolve_fqn
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self, init_value: int):
        self.init_value = init_value

    def handle(self, command: CommandTest) -> None:
        pass


class TestPypendencyBusStopResolver(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.command_handler_fqn = resolve_fqn(CommandTestHandler)
        cls.test_init_value = 324
        cls.pypendency_container = Container(
            [
                Definition(
                    identifier=cls.command_handler_fqn,
                    fully_qualified_name=cls.command_handler_fqn,
                    arguments=[Argument.no_kw_argument(cls.test_init_value)],
                )
            ]
        )

    def setUp(self) -> None:
        self.pypendency_bus_stop_resolver = PypendencyBusStopResolver(self.pypendency_container)

    def test_resolve__success(self):
        resolved_command_handler = self.pypendency_bus_stop_resolver.resolve(self.command_handler_fqn)

        self.assertIsInstance(resolved_command_handler, CommandTestHandler)
        self.assertEqual(resolved_command_handler.init_value, self.test_init_value)