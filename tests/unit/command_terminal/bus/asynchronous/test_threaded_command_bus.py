from threading import Thread
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.bus.asynchronous.threaded_command_bus import ThreadedCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.middleware.command_middleware_executor import CommandMiddlewareExecutor
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry


class TestThreadedCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_registry_mock = Mock(spec=InMemoryCommandRegistry)
        self.threaded_command_bus = ThreadedCommandBus(self.command_registry_mock)

    def test_execute_not_registered(self):
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_command_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.threaded_command_bus.execute(test_command)

        self.assertEqual(test_command.__class__.__name__, hnffc.exception.command_name)
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with(test_command.__class__)

    @patch.object(CommandMiddlewareExecutor, "execute")
    @patch("bus_station.command_terminal.bus.asynchronous.threaded_command_bus.Thread")
    def test_execute_success(self, thread_mock, middleware_executor_mock):
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)
        test_thread = Mock(spec=Thread)
        thread_mock.return_value = test_thread
        self.command_registry_mock.get_command_destination_contact.return_value = test_command_handler

        self.threaded_command_bus.execute(test_command)

        thread_mock.assert_called_once_with(target=middleware_executor_mock, args=(test_command, test_command_handler))
        test_thread.start.assert_called_once_with()
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with(test_command.__class__)
