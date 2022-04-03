from http.server import ThreadingHTTPServer
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from jsonrpcserver import Error, Success
from jsonrpcserver.codes import ERROR_INTERNAL_ERROR

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.json_rpc_command_server import JsonRPCCommandServer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer


class TestJsonRPCCommandServer(TestCase):
    def setUp(self) -> None:
        self.passenger_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.command_receiver_mock = Mock(spec=PassengerReceiver[Command, CommandHandler])
        self.json_rpc_server = JsonRPCCommandServer(self.passenger_deserializer_mock, self.command_receiver_mock)

    @patch("bus_station.shared_terminal.json_rpc_server.partial")
    def test_register(self, partial_mock):
        test_command_class = Mock(spec=Command)
        test_command_class.__name__ = "test_name"
        test_command_handler = Mock(spec=CommandHandler)

        self.json_rpc_server.register(test_command_class, test_command_handler)

        partial_mock.assert_called_once_with(
            self.json_rpc_server.passenger_handler, test_command_handler, test_command_class
        )

    @patch("bus_station.shared_terminal.json_rpc_server.method")
    @patch("bus_station.shared_terminal.json_rpc_server.RequestHandler")
    @patch("bus_station.shared_terminal.json_rpc_server.partial")
    @patch("bus_station.shared_terminal.json_rpc_server.ThreadingHTTPServer")
    def test_run(self, http_server_mock, partial_mock, request_handler_mock, method_mock):
        test_command_class = Mock(spec=Command)
        test_command_class.__name__ = "test_name"
        test_command_handler = Mock(spec=CommandHandler)
        self.json_rpc_server.register(test_command_class, test_command_handler)
        test_http_server = Mock(spec=ThreadingHTTPServer)
        http_server_mock.return_value = test_http_server
        test_port = 7456

        self.json_rpc_server.run(test_port)

        partial_mock.assert_called_once_with(
            self.json_rpc_server.passenger_handler, test_command_handler, test_command_class
        )
        method_mock.assert_called_once_with(partial_mock(), name=test_command_class.__name__)
        http_server_mock.assert_called_once_with(("127.0.0.1", test_port), request_handler_mock)
        test_http_server.serve_forever.assert_called_once_with()

    def test_passenger_handling_success(self):
        test_serialized_command = "test_serialized_command"
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)
        self.passenger_deserializer_mock.deserialize.return_value = test_command

        json_rpc_response = self.json_rpc_server.passenger_handler(
            test_command_handler, test_command.__class__, test_serialized_command
        )

        expected_rpc_response = Success(result=None)
        self.assertEqual(expected_rpc_response, json_rpc_response)
        self.passenger_deserializer_mock.deserialize.assert_called_once_with(
            test_serialized_command, passenger_cls=test_command.__class__
        )
        self.command_receiver_mock.receive.assert_called_once_with(test_command, test_command_handler)

    def test_passenger_handling_error(self):
        test_serialized_command = "test_serialized_command"
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)
        self.passenger_deserializer_mock.deserialize.return_value = test_command
        test_exception = Exception("test_exception")
        self.command_receiver_mock.receive.side_effect = test_exception

        json_rpc_response = self.json_rpc_server.passenger_handler(
            test_command_handler, test_command.__class__, test_serialized_command
        )

        expected_rpc_response = Error(code=ERROR_INTERNAL_ERROR, message=str(test_exception))
        self.assertEqual(expected_rpc_response, json_rpc_response)
        self.passenger_deserializer_mock.deserialize.assert_called_once_with(
            test_serialized_command, passenger_cls=test_command.__class__
        )
        self.command_receiver_mock.receive.assert_called_once_with(test_command, test_command_handler)

    def test_passenger_handling_not_command(self):
        test_not_command = MagicMock()
        test_command_handler = Mock(spec=CommandHandler)
        test_serialized_not_command = "test_serialized_not_command"
        self.passenger_deserializer_mock.deserialize.return_value = test_not_command

        json_rpc_response = self.json_rpc_server.passenger_handler(
            test_command_handler, test_not_command.__class__, test_serialized_not_command
        )

        expected_rpc_response = Error(code=ERROR_INTERNAL_ERROR, message="Input serialized command is not a Command")
        self.assertEqual(expected_rpc_response, json_rpc_response)
        self.passenger_deserializer_mock.deserialize.assert_called_once_with(
            test_serialized_not_command, passenger_cls=test_not_command.__class__
        )
