from multiprocessing.context import Process
from unittest import TestCase
from unittest.mock import Mock, patch

from jsonrpcclient import Error
from jsonrpcserver import Success
from requests import Response

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus import JsonRPCCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_execution_failed import CommandExecutionFailed
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.json_rpc_server import JsonRPCServer


class TestJsonRPCCommandBus(TestCase):
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.JsonRPCCommandServer")
    def setUp(self, json_rpc_server_builder_mock) -> None:
        self.command_serializer_mock = Mock(spec=PassengerSerializer)
        self.command_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.command_registry_mock = Mock(spec=RemoteCommandRegistry)
        self.test_host = "test_host"
        self.test_port = 1234
        self.json_rpc_server_mock = Mock(spec=JsonRPCServer)
        json_rpc_server_builder_mock.return_value = self.json_rpc_server_mock
        self.command_receiver_mock = Mock(spec=PassengerReceiver[Command, CommandBus])
        self.json_rpc_command_bus = JsonRPCCommandBus(
            self.test_host,
            self.test_port,
            self.command_serializer_mock,
            self.command_deserializer_mock,
            self.command_registry_mock,
            self.command_receiver_mock,
        )

    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.Process")
    def test_start(self, process_mock):
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_commands_registered.return_value = [test_command.__class__]
        test_command_handler = Mock(spec=CommandHandler)
        self.command_registry_mock.get_command_destination.return_value = test_command_handler

        self.json_rpc_command_bus.start()

        process_mock.assert_called_once_with(target=self.json_rpc_server_mock.run, args=(self.test_port,))
        test_process.start.assert_called_once_with()
        self.json_rpc_server_mock.register.assert_called_once_with(test_command.__class__, test_command_handler)
        self.command_registry_mock.get_command_destination.assert_called_once_with(test_command.__class__)
        self.command_registry_mock.get_commands_registered.assert_called_once_with()

    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.signal")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.os")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.Process")
    def test_stop(self, process_mock, os_mock, signal_mock):
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        self.command_registry_mock.get_commands_registered.return_value = []
        self.json_rpc_command_bus.start()

        self.json_rpc_command_bus.stop()

        process_mock.assert_called_once_with(target=self.json_rpc_server_mock.run, args=(self.test_port,))
        test_process.start.assert_called_once_with()
        os_mock.kill.assert_called_once_with(test_process.pid, signal_mock.SIGINT)
        test_process.join.assert_called_once_with()

    def test_transport_not_registered(self):
        test_command = Mock(spec=Command, name="TestCommand")
        self.command_registry_mock.get_command_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.json_rpc_command_bus.transport(test_command)

        self.assertEqual(test_command.__class__.__name__, hnffc.exception.command_name)
        self.command_serializer_mock.serialize.assert_not_called()
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with(test_command.__class__)

    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.to_result")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.request")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.requests")
    def test_transport_success(self, requests_mock, request_mock, to_result_mock):
        test_command = Mock(spec=Command, name="TestCommand")
        test_host = "test_host"
        test_port = "41124"
        test_command_handler_addr = f"{test_host}:{test_port}"
        self.command_registry_mock.get_command_destination_contact.return_value = test_command_handler_addr
        test_serialized_command = "test_serialized_command"
        self.command_serializer_mock.serialize.return_value = test_serialized_command
        test_json_rpc_request = {"test": "test"}
        request_mock.return_value = test_json_rpc_request
        test_requests_response = Mock(spec=Response)
        test_json_requests_response = {"test_response": "test_response"}
        test_requests_response.json.return_value = test_json_requests_response
        test_json_rpc_success_response = Mock(spec=Success)
        to_result_mock.return_value = test_json_rpc_success_response
        requests_mock.post.return_value = test_requests_response

        self.json_rpc_command_bus.transport(test_command)

        self.command_serializer_mock.serialize.assert_called_once_with(test_command)
        request_mock.assert_called_once_with(test_command.__class__.__name__, params=(test_serialized_command,))
        requests_mock.post.assert_called_once_with(test_command_handler_addr, json=test_json_rpc_request)
        to_result_mock.assert_called_once_with(test_json_requests_response)

    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.to_result")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.request")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.requests")
    def test_transport_error(self, requests_mock, request_mock, to_result_mock):
        test_command = Mock(spec=Command, name="TestCommand")
        test_host = "test_host"
        test_port = "41124"
        test_command_handler_addr = f"{test_host}:{test_port}"
        self.command_registry_mock.get_command_destination_contact.return_value = test_command_handler_addr
        test_serialized_command = "test_serialized_command"
        self.command_serializer_mock.serialize.return_value = test_serialized_command
        test_json_rpc_request = {"test": "test"}
        request_mock.return_value = test_json_rpc_request
        test_requests_response = Mock(spec=Response)
        test_json_requests_response = {"test_response": "test_response"}
        test_requests_response.json.return_value = test_json_requests_response
        test_error_message = "test_error_message"
        test_json_rpc_error_response = Mock(spec=Error, message=test_error_message)
        to_result_mock.return_value = test_json_rpc_error_response
        requests_mock.post.return_value = test_requests_response

        with self.assertRaises(CommandExecutionFailed) as cef:
            self.json_rpc_command_bus.transport(test_command)

        self.assertEqual(test_command, cef.exception.command)
        self.assertEqual(test_error_message, cef.exception.reason)
        self.command_serializer_mock.serialize.assert_called_once_with(test_command)
        request_mock.assert_called_once_with(test_command.__class__.__name__, params=(test_serialized_command,))
        requests_mock.post.assert_called_once_with(test_command_handler_addr, json=test_json_rpc_request)
        to_result_mock.assert_called_once_with(test_json_requests_response)
