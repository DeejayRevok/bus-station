from typing import Callable
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.bus.synchronous.sync_command_bus import SyncCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_for_command_already_registered import HandlerForCommandAlreadyRegistered
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.middleware.command_middleware_executor import CommandMiddlewareExecutor
from bus_station.passengers.registry.in_memory_passenger_record_repository import InMemoryRegistry


class TestSyncCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_registry_mock = Mock(spec=InMemoryRegistry)
        self.sync_command_bus = SyncCommandBus(self.command_registry_mock)

    @patch("bus_station.command_terminal.bus.command_bus.get_type_hints")
    def test_register_already_registered(self, get_type_hints_mock):
        test_command_handler = Mock(spec=CommandHandler)
        test_command = Mock(spec=Command)
        get_type_hints_mock.return_value = {"command": test_command.__class__}
        self.command_registry_mock.__contains__ = Mock(spec=Callable)
        self.command_registry_mock.__contains__.return_value = True

        with self.assertRaises(HandlerForCommandAlreadyRegistered) as hfcar:
            self.sync_command_bus.register(test_command_handler)

        self.assertEqual(test_command.__class__.__name__, hfcar.exception.command_name)
        self.command_registry_mock.__contains__.assert_called_once_with(test_command.__class__)

    @patch("bus_station.command_terminal.bus.command_bus.get_type_hints")
    def test_register_success(self, get_type_hints_mock):
        test_command_handler = Mock(spec=CommandHandler)
        test_command = Mock(spec=Command)
        get_type_hints_mock.return_value = {"command": test_command.__class__}
        self.command_registry_mock.__contains__ = Mock(spec=Callable)
        self.command_registry_mock.__contains__.return_value = False

        self.sync_command_bus.register(test_command_handler)

        self.command_registry_mock.__contains__.assert_called_once_with(test_command.__class__)
        self.command_registry_mock.register.assert_called_once_with(test_command.__class__, test_command_handler)

    def test_execute_not_registered(self):
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_passenger_destination.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.sync_command_bus.execute(test_command)

        self.assertEqual(test_command.__class__.__name__, hnffc.exception.command_name)
        self.command_registry_mock.get_passenger_destination.assert_called_once_with(test_command.__class__)

    @patch("bus_station.command_terminal.bus.command_bus.get_type_hints")
    @patch.object(CommandMiddlewareExecutor, "execute")
    def test_execute_success(self, middleware_executor_mock, get_type_hints_mock):
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)
        get_type_hints_mock.return_value = {"command": test_command.__class__}
        self.command_registry_mock.get_passenger_destination.return_value = test_command_handler

        self.sync_command_bus.execute(test_command)

        middleware_executor_mock.assert_called_once_with(test_command, test_command_handler)
        self.command_registry_mock.get_passenger_destination.assert_called_once_with(test_command.__class__)
