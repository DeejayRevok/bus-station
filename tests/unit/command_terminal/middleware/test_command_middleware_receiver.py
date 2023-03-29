from typing import Type
from unittest import TestCase
from unittest.mock import Mock, call, patch

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware import CommandMiddleware
from bus_station.command_terminal.middleware.command_middleware_receiver import CommandMiddlewareReceiver


class TestCommandMiddlewareReceiver(TestCase):
    def setUp(self) -> None:
        self.command_middleware_receiver = CommandMiddlewareReceiver()

    def test_add_middleware_definition_lazy(self):
        test_middleware_class = Mock(spec=CommandMiddleware.__class__)
        test_arg = "test_arg"

        self.command_middleware_receiver.add_middleware_definition(test_middleware_class, test_arg, lazy=True)

        test_middleware_class.assert_not_called()

    def test_add_middleware_definition_not_lazy(self):
        test_middleware_class = Mock(spec=CommandMiddleware.__class__)
        test_arg = "test_arg"

        self.command_middleware_receiver.add_middleware_definition(test_middleware_class, test_arg, lazy=False)

        test_middleware_class.assert_called_once_with(test_arg)

    @patch("bus_station.passengers.reception.passenger_receiver.set_context_root_passenger_id")
    def test_receive_successful_handle(self, set_context_root_passenger_id_mock):
        parent_mock = Mock()
        test_middleware1_class = Mock(spec=Type[CommandMiddleware])
        test_middleware2_class = Mock(spec=Type[CommandMiddleware])
        test_command = Mock(spec=Command, passenger_id="test_passenger_id", root_passenger_id="test_root_passenger_id")
        test_command_handler = Mock(spec=CommandHandler)
        parent_mock.middleware1_class = test_middleware1_class
        parent_mock.middleware2_class = test_middleware2_class
        parent_mock.handler = test_command_handler

        self.command_middleware_receiver.add_middleware_definition(test_middleware1_class)
        self.command_middleware_receiver.add_middleware_definition(test_middleware2_class)
        self.command_middleware_receiver.receive(test_command, test_command_handler)

        parent_mock.assert_has_calls(
            [
                call.middleware1_class().before_handle(test_command, test_command_handler),
                call.middleware2_class().before_handle(test_command, test_command_handler),
                call.handler.handle(test_command),
                call.middleware2_class().after_handle(test_command, test_command_handler, handling_exception=None),
                call.middleware1_class().after_handle(test_command, test_command_handler, handling_exception=None),
            ]
        )
        set_context_root_passenger_id_mock.assert_has_calls(
            [call(test_command.passenger_id), call(test_command.root_passenger_id)]
        )

    @patch("bus_station.passengers.reception.passenger_receiver.set_context_root_passenger_id")
    def test_receive_handle_exception(self, set_context_root_passenger_id_mock):
        parent_mock = Mock()
        test_middleware1_class = Mock(spec=Type[CommandMiddleware])
        test_middleware2_class = Mock(spec=Type[CommandMiddleware])
        test_command = Mock(spec=Command, passenger_id="test_passenger_id", root_passenger_id="test_root_passenger_id")
        test_command_handler = Mock(spec=CommandHandler)
        parent_mock.middleware1_class = test_middleware1_class
        parent_mock.middleware2_class = test_middleware2_class
        parent_mock.handler = test_command_handler
        handle_exception = Exception("Test handle exception")
        test_command_handler.handle.side_effect = handle_exception
        self.command_middleware_receiver.add_middleware_definition(test_middleware1_class)
        self.command_middleware_receiver.add_middleware_definition(test_middleware2_class)

        with self.assertRaises(Exception) as context:
            self.command_middleware_receiver.receive(test_command, test_command_handler)

        self.assertEqual(handle_exception, context.exception)
        parent_mock.assert_has_calls(
            [
                call.middleware1_class().before_handle(test_command, test_command_handler),
                call.middleware2_class().before_handle(test_command, test_command_handler),
                call.handler.handle(test_command),
                call.middleware2_class().after_handle(
                    test_command, test_command_handler, handling_exception=handle_exception
                ),
                call.middleware1_class().after_handle(
                    test_command, test_command_handler, handling_exception=handle_exception
                ),
            ]
        )
        set_context_root_passenger_id_mock.assert_has_calls(
            [call(test_command.passenger_id), call(test_command.root_passenger_id)]
        )
