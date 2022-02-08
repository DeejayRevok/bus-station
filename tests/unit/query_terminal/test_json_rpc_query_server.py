from http.server import ThreadingHTTPServer
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from jsonrpcserver import Error, Success
from jsonrpcserver.codes import ERROR_INTERNAL_ERROR

from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.query_terminal.json_rpc_query_server import JsonRPCQueryServer
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.serialization.query_response_serializer import QueryResponseSerializer


class TestJsonRPCQueryServer(TestCase):
    def setUp(self) -> None:
        self.passenger_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.passenger_middleware_executor_mock = Mock(spec=PassengerMiddlewareExecutor)
        self.query_response_serializer_mock = Mock(spec=QueryResponseSerializer)
        self.json_rpc_server = JsonRPCQueryServer(
            self.passenger_deserializer_mock,
            self.passenger_middleware_executor_mock,
            self.query_response_serializer_mock,
        )

    @patch("bus_station.shared_terminal.json_rpc_server.partial")
    def test_register(self, partial_mock):
        test_query_class = Mock(spec=Query)
        test_query_class.__name__ = "test_name"
        test_query_handler = Mock(spec=QueryHandler)

        self.json_rpc_server.register(test_query_class, test_query_handler)

        partial_mock.assert_called_once_with(
            self.json_rpc_server.passenger_executor, test_query_handler, test_query_class
        )

    @patch("bus_station.shared_terminal.json_rpc_server.method")
    @patch("bus_station.shared_terminal.json_rpc_server.RequestHandler")
    @patch("bus_station.shared_terminal.json_rpc_server.partial")
    @patch("bus_station.shared_terminal.json_rpc_server.ThreadingHTTPServer")
    def test_run(self, http_server_mock, partial_mock, request_handler_mock, method_mock):
        test_query_class = Mock(spec=Query)
        test_query_class.__name__ = "test_name"
        test_query_handler = Mock(spec=QueryHandler)
        self.json_rpc_server.register(test_query_class, test_query_handler)
        test_http_server = Mock(spec=ThreadingHTTPServer)
        http_server_mock.return_value = test_http_server
        test_port = 7456

        self.json_rpc_server.run(test_port)

        partial_mock.assert_called_once_with(
            self.json_rpc_server.passenger_executor, test_query_handler, test_query_class
        )
        method_mock.assert_called_once_with(partial_mock(), name=test_query_class.__name__)
        http_server_mock.assert_called_once_with(("127.0.0.1", test_port), request_handler_mock)
        test_http_server.serve_forever.assert_called_once_with()

    def test_passenger_executor_success(self):
        test_serialized_query = "test_serialized_query"
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)
        self.passenger_deserializer_mock.deserialize.return_value = test_query
        test_query_response = Mock(spec=QueryResponse)
        self.passenger_middleware_executor_mock.execute.return_value = test_query_response
        test_query_response_serialized = {"test": "test"}
        self.query_response_serializer_mock.serialize.return_value = test_query_response_serialized

        json_rpc_query_response = self.json_rpc_server.passenger_executor(
            test_query_handler, test_query.__class__, test_serialized_query
        )

        expected_rpc_response = Success(result=test_query_response_serialized)
        self.assertEqual(expected_rpc_response, json_rpc_query_response)
        self.passenger_deserializer_mock.deserialize.assert_called_once_with(
            test_serialized_query, passenger_cls=test_query.__class__
        )
        self.passenger_middleware_executor_mock.execute.assert_called_once_with(test_query, test_query_handler)

    def test_passenger_executor_error(self):
        test_serialized_query = "test_serialized_query"
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)
        self.passenger_deserializer_mock.deserialize.return_value = test_query
        test_exception = Exception("test_exception")
        self.passenger_middleware_executor_mock.execute.side_effect = test_exception

        json_rpc_response = self.json_rpc_server.passenger_executor(
            test_query_handler, test_query.__class__, test_serialized_query
        )

        expected_rpc_response = Error(code=ERROR_INTERNAL_ERROR, message=str(test_exception))
        self.assertEqual(expected_rpc_response, json_rpc_response)
        self.passenger_deserializer_mock.deserialize.assert_called_once_with(
            test_serialized_query, passenger_cls=test_query.__class__
        )
        self.passenger_middleware_executor_mock.execute.assert_called_once_with(test_query, test_query_handler)

    def test_passenger_executor_not_query(self):
        test_not_query = MagicMock()
        test_query_handler = Mock(spec=QueryHandler)
        test_serialized_not_query = "test_serialized_not_query"
        self.passenger_deserializer_mock.deserialize.return_value = test_not_query

        json_rpc_response = self.json_rpc_server.passenger_executor(
            test_query_handler, test_not_query.__class__, test_serialized_not_query
        )

        expected_rpc_response = Error(code=ERROR_INTERNAL_ERROR, message="Input serialized query is not a Query")
        self.assertEqual(expected_rpc_response, json_rpc_response)
        self.passenger_deserializer_mock.deserialize.assert_called_once_with(
            test_serialized_not_query, passenger_cls=test_not_query.__class__
        )
