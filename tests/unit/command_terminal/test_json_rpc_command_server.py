from http.server import ThreadingHTTPServer
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.json_rpc_command_server import JsonRPCCommandServer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer


class TestJsonRPCCommandServer(TestCase):
    def setUp(self) -> None:
        self.passenger_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.command_receiver_mock = Mock(spec=PassengerReceiver)
        self.port = 1233
        self.json_rpc_server = JsonRPCCommandServer(
            self.port, self.passenger_deserializer_mock, self.command_receiver_mock
        )

    @patch("bus_station.shared_terminal.json_rpc_server.partial")
    def test_register(self, partial_mock):
        test_command_class = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)

        self.json_rpc_server.register(test_command_class, test_command_handler)

        partial_mock.assert_called_once()

    @patch("bus_station.shared_terminal.json_rpc_server.method")
    @patch("bus_station.shared_terminal.json_rpc_server.RequestHandler")
    @patch("bus_station.shared_terminal.json_rpc_server.partial")
    @patch("bus_station.shared_terminal.json_rpc_server.ThreadingHTTPServer")
    def test_run(self, http_server_mock, partial_mock, request_handler_mock, method_mock):
        test_command_class = Mock(spec=Command)
        test_command_class.passenger_name.return_value = "test_name"
        test_command_handler = Mock(spec=CommandHandler)
        self.json_rpc_server.register(test_command_class, test_command_handler)
        test_http_server = Mock(spec=ThreadingHTTPServer)
        http_server_mock.return_value = test_http_server

        self.json_rpc_server.run()

        partial_mock.assert_called_once()
        method_mock.assert_called_once_with(partial_mock(), name="test_name")
        http_server_mock.assert_called_once_with(("127.0.0.1", self.port), request_handler_mock)
        test_http_server.serve_forever.assert_called_once_with()
