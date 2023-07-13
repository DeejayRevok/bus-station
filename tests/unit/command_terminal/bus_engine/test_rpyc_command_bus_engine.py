from unittest import TestCase
from unittest.mock import Mock

from bus_station.command_terminal.bus_engine.rpyc_command_bus_engine import RPyCCommandBusEngine
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_not_found import CommandHandlerNotFound
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.command_terminal.rpyc_command_server import RPyCServer


class TestRPyCCommandBusEngine(TestCase):
    def setUp(self):
        self.server = Mock(spec=RPyCServer)
        self.registry = Mock(spec=CommandHandlerRegistry)

    def test_initialize_registers_command_handler_in_server(self):
        handler = Mock(spec=CommandHandler)
        handler_name = "handler_name"
        self.registry.get_bus_stop_by_name.return_value = handler
        test_command_mock = Mock(spec=Command)
        handler.passenger.return_value = test_command_mock

        RPyCCommandBusEngine(self.server, self.registry, handler_name)

        self.registry.get_bus_stop_by_name.assert_called_once_with(handler_name)
        self.server.register.assert_called_once_with(test_command_mock, handler)

    def test_initialize_raises_exception_if_command_handler_not_found(self):
        handler_name = "handler_name"
        self.registry.get_bus_stop_by_name.return_value = None

        with self.assertRaises(CommandHandlerNotFound) as context:
            RPyCCommandBusEngine(self.server, self.registry, handler_name)

        self.assertEqual(handler_name, context.exception.command_handler_name)
        self.registry.get_bus_stop_by_name.assert_called_once_with(handler_name)

    def test_start_runs_the_server(self):
        handler_name = "handler_name"
        engine = RPyCCommandBusEngine(self.server, self.registry, handler_name)

        engine.start()

        self.server.run.assert_called_once()
