from unittest import TestCase
from unittest.mock import Mock, patch

from jsonrpcclient import Error
from jsonrpcserver import Success
from requests import Response

from bus_station.bus_stop.registration.address.address_not_found_for_passenger import AddressNotFoundForPassenger
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus import JsonRPCCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_execution_failed import CommandExecutionFailed
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class TestJsonRPCCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_serializer_mock = Mock(spec=PassengerSerializer)
        self.address_registry_mock = Mock(spec=BusStopAddressRegistry)
        self.json_rpc_command_bus = JsonRPCCommandBus(
            self.command_serializer_mock,
            self.address_registry_mock,
        )

    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    def test_transport_passenger_address_not_found(self, get_context_root_passenger_id_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.return_value = None

        with self.assertRaises(AddressNotFoundForPassenger) as anffp:
            self.json_rpc_command_bus.transport(test_command)

        self.assertEqual("test_command", anffp.exception.passenger_name)
        self.command_serializer_mock.serialize.assert_not_called()
        test_command.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.assert_called_once_with(
            test_command.__class__
        )

    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.parse")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.request")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.requests")
    def test_transport_success(self, requests_mock, request_mock, to_result_mock, get_context_root_passenger_id_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        test_host = "test_host"
        test_port = "41124"
        test_command_handler_addr = f"{test_host}:{test_port}"
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.return_value = f"{test_host}:{test_port}"
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
        test_command.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.assert_called_once_with(
            test_command.__class__
        )

    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.parse")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.request")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.json_rpc_command_bus.requests")
    def test_transport_error(self, requests_mock, request_mock, to_result_mock, get_context_root_passenger_id_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        test_host = "test_host"
        test_port = "41124"
        test_command_handler_addr = f"{test_host}:{test_port}"
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.return_value = f"{test_host}:{test_port}"
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
        test_command.set_root_passenger_id.assert_called_once_with("test_root_passenger_id_id")
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.assert_called_once_with(
            test_command.__class__
        )
