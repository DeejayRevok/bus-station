from unittest import TestCase
from unittest.mock import Mock, patch

from jsonrpcclient import Error
from jsonrpcserver import Success
from requests import Response

from bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus import JsonRPCCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_execution_failed import CommandExecutionFailed
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class TestJsonRPCCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_serializer_mock = Mock(spec=PassengerSerializer)
        self.command_registry_mock = Mock(spec=RemoteCommandRegistry)
        self.json_rpc_command_bus = JsonRPCCommandBus(
            self.command_serializer_mock,
            self.command_registry_mock,
        )

    @patch("bus_station.shared_terminal.bus.get_distributed_id")
    def test_transport_not_registered(self, get_distributed_id_mock):
        get_distributed_id_mock.return_value = "test_distributed_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        self.command_registry_mock.get_command_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.json_rpc_command_bus.transport(test_command)

        self.assertEqual("test_command", hnffc.exception.command_name)
        self.command_serializer_mock.serialize.assert_not_called()
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with("test_command")
        test_command.set_distributed_id.assert_called_once_with("test_distributed_id")

    @patch("bus_station.shared_terminal.bus.get_distributed_id")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.parse")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.request")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.requests")
    def test_transport_success(self, requests_mock, request_mock, to_result_mock, get_distributed_id_mock):
        get_distributed_id_mock.return_value = "test_distributed_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
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
        request_mock.assert_called_once_with(
            "command.bus_station.command_terminal.command.Command", params=(test_serialized_command,)
        )
        requests_mock.post.assert_called_once_with(test_command_handler_addr, json=test_json_rpc_request)
        to_result_mock.assert_called_once_with(test_json_requests_response)
        test_command.set_distributed_id.assert_called_once_with("test_distributed_id")

    @patch("bus_station.shared_terminal.bus.get_distributed_id")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.parse")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.request")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.requests")
    def test_transport_error(self, requests_mock, request_mock, to_result_mock, get_distributed_id_mock):
        get_distributed_id_mock.return_value = "test_distributed_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
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
        request_mock.assert_called_once_with(
            "command.bus_station.command_terminal.command.Command", params=(test_serialized_command,)
        )
        requests_mock.post.assert_called_once_with(test_command_handler_addr, json=test_json_rpc_request)
        to_result_mock.assert_called_once_with(test_json_requests_response)
        test_command.set_distributed_id.assert_called_once_with("test_distributed_id")
