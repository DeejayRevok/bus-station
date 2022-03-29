from typing import Type
from unittest import TestCase
from unittest.mock import Mock, call

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware import CommandMiddleware
from bus_station.command_terminal.middleware.command_middleware_executor import CommandMiddlewareExecutor


class TestCommandMiddlewareExecutor(TestCase):
    def setUp(self) -> None:
        self.command_middleware_executor = CommandMiddlewareExecutor()

    def test_execute_success(self):
        parent_mock = Mock()
        test_middleware1_class = Mock(spec=Type[CommandMiddleware])
        test_middleware2_class = Mock(spec=Type[CommandMiddleware])
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)
        parent_mock.middleware1_class = test_middleware1_class
        parent_mock.middleware2_class = test_middleware2_class
        parent_mock.handler = test_command_handler

        self.command_middleware_executor.add_middleware_definition(test_middleware1_class)
        self.command_middleware_executor.add_middleware_definition(test_middleware2_class)
        self.command_middleware_executor.execute(test_command, test_command_handler)

        parent_mock.assert_has_calls(
            [
                call.middleware1_class().before_handle(test_command, test_command_handler),
                call.middleware2_class().before_handle(test_command, test_command_handler),
                call.handler.handle(test_command),
                call.middleware2_class().after_handle(test_command, test_command_handler),
                call.middleware1_class().after_handle(test_command, test_command_handler),
            ]
        )
