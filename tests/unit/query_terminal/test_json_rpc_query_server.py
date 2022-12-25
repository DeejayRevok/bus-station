from http.server import ThreadingHTTPServer
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.query_terminal.json_rpc_query_server import JsonRPCQueryServer
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.serialization.query_response_serializer import QueryResponseSerializer


class TestJsonRPCQueryServer(TestCase):
    def setUp(self) -> None:
        self.passenger_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.query_receiver_mock = Mock(spec=PassengerReceiver[Query, QueryHandler])
        self.query_response_serializer_mock = Mock(spec=QueryResponseSerializer)
        self.port = 123
        self.json_rpc_server = JsonRPCQueryServer(
            self.port,
            self.passenger_deserializer_mock,
            self.query_receiver_mock,
            self.query_response_serializer_mock,
        )

    @patch("bus_station.shared_terminal.json_rpc_server.partial")
    def test_register(self, partial_mock):
        test_query_class = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)

        self.json_rpc_server.register(test_query_class, test_query_handler)

        partial_mock.assert_called_once()

    @patch("bus_station.shared_terminal.json_rpc_server.method")
    @patch("bus_station.shared_terminal.json_rpc_server.RequestHandler")
    @patch("bus_station.shared_terminal.json_rpc_server.partial")
    @patch("bus_station.shared_terminal.json_rpc_server.ThreadingHTTPServer")
    def test_run(self, http_server_mock, partial_mock, request_handler_mock, method_mock):
        test_query_class = Mock(spec=Query)
        test_query_class.passenger_name.return_value = "test_name"
        test_query_handler = Mock(spec=QueryHandler)
        self.json_rpc_server.register(test_query_class, test_query_handler)
        test_http_server = Mock(spec=ThreadingHTTPServer)
        http_server_mock.return_value = test_http_server

        self.json_rpc_server.run()

        partial_mock.assert_called_once()
        method_mock.assert_called_once_with(partial_mock(), name="test_name")
        http_server_mock.assert_called_once_with(("127.0.0.1", self.port), request_handler_mock)
        test_http_server.serve_forever.assert_called_once_with()
