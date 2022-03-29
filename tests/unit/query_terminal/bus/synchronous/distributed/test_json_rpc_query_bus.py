from multiprocessing.context import Process
from unittest import TestCase
from unittest.mock import Mock, patch

from jsonrpcclient import Error
from jsonrpcserver import Success
from requests import Response

from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus import JsonRPCQueryBus
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_execution_failed import QueryExecutionFailed
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.remote_query_registry import RemoteQueryRegistry
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer
from bus_station.query_terminal.serialization.query_response_serializer import QueryResponseSerializer
from bus_station.shared_terminal.json_rpc_server import JsonRPCServer


class TestJsonRPCQueryBus(TestCase):
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.JsonRPCQueryServer")
    def setUp(self, json_rpc_server_builder_mock) -> None:
        self.query_serializer_mock = Mock(spec=PassengerSerializer)
        self.query_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.query_response_serializer_mock = Mock(spec=QueryResponseSerializer)
        self.query_response_deserializer_mock = Mock(spec=QueryResponseDeserializer)
        self.query_registry_mock = Mock(spec=RemoteQueryRegistry)
        self.middleware_executor_mock = Mock(spec=PassengerMiddlewareExecutor)
        self.test_host = "test_host"
        self.test_port = 1234
        self.json_rpc_server_mock = Mock(spec=JsonRPCServer)
        json_rpc_server_builder_mock.return_value = self.json_rpc_server_mock
        self.json_rpc_query_bus = JsonRPCQueryBus(
            self.test_host,
            self.test_port,
            self.query_serializer_mock,
            self.query_deserializer_mock,
            self.query_response_serializer_mock,
            self.query_response_deserializer_mock,
            self.query_registry_mock,
        )
        self.json_rpc_query_bus._middleware_executor = self.middleware_executor_mock

    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.Process")
    def test_start(self, process_mock):
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_query = Mock(spec=Query)
        self.query_registry_mock.get_queries_registered.return_value = [test_query.__class__]
        test_query_handler = Mock(spec=QueryHandler)
        self.query_registry_mock.get_query_destination.return_value = test_query_handler

        self.json_rpc_query_bus.start()

        process_mock.assert_called_once_with(target=self.json_rpc_server_mock.run, args=(self.test_port,))
        test_process.start.assert_called_once_with()

    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.signal")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.os")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.Process")
    def test_stop(self, process_mock, os_mock, signal_mock):
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        self.query_registry_mock.get_queries_registered.return_value = []
        self.json_rpc_query_bus.start()

        self.json_rpc_query_bus.stop()

        process_mock.assert_called_once_with(target=self.json_rpc_server_mock.run, args=(self.test_port,))
        test_process.start.assert_called_once_with()
        os_mock.kill.assert_called_once_with(test_process.pid, signal_mock.SIGINT)
        test_process.join.assert_called_once_with()

    def test_execute_not_registered(self):
        test_query = Mock(spec=Query, name="TestQuery")
        self.query_registry_mock.get_query_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForQuery) as hnffq:
            self.json_rpc_query_bus.execute(test_query)

        self.assertEqual(test_query.__class__.__name__, hnffq.exception.query_name)
        self.query_serializer_mock.serialize.assert_not_called()
        self.query_registry_mock.get_query_destination_contact.assert_called_once_with(test_query.__class__)

    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.to_result")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.request")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.requests")
    def test_execute_success(self, requests_mock, request_mock, to_result_mock):
        test_query = Mock(spec=Query, name="TestQuery")
        test_host = "test_host"
        test_port = "41124"
        test_query_handler_addr = f"{test_host}:{test_port}"
        self.query_registry_mock.get_query_destination_contact.return_value = test_query_handler_addr
        test_serialized_query = "test_serialized_query"
        self.query_serializer_mock.serialize.return_value = test_serialized_query
        test_json_rpc_request = {"test": "test"}
        request_mock.return_value = test_json_rpc_request
        test_requests_response = Mock(spec=Response)
        test_json_requests_response = {"test_response": "test_response"}
        test_requests_response.json.return_value = test_json_requests_response
        test_query_response_serialized = {"test_result": "test_result"}
        test_json_rpc_success_response = Mock(spec=Success, result=test_query_response_serialized)
        to_result_mock.return_value = test_json_rpc_success_response
        requests_mock.post.return_value = test_requests_response
        test_query_response = Mock(spec=QueryResponse)
        self.query_response_deserializer_mock.deserialize.return_value = test_query_response

        query_response = self.json_rpc_query_bus.execute(test_query)

        self.assertEqual(test_query_response, query_response)
        self.query_serializer_mock.serialize.assert_called_once_with(test_query)
        request_mock.assert_called_once_with(test_query.__class__.__name__, params=(test_serialized_query,))
        requests_mock.post.assert_called_once_with(test_query_handler_addr, json=test_json_rpc_request)
        to_result_mock.assert_called_once_with(test_json_requests_response)
        self.query_response_deserializer_mock.deserialize.assert_called_once_with(test_query_response_serialized)

    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.to_result")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.request")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.requests")
    def test_execute_error(self, requests_mock, request_mock, to_result_mock):
        test_query = Mock(spec=Query, name="TestQuery")
        test_host = "test_host"
        test_port = "41124"
        test_query_handler_addr = f"{test_host}:{test_port}"
        self.query_registry_mock.get_query_destination_contact.return_value = test_query_handler_addr
        test_serialized_query = "test_serialized_query"
        self.query_serializer_mock.serialize.return_value = test_serialized_query
        test_json_rpc_request = {"test": "test"}
        request_mock.return_value = test_json_rpc_request
        test_requests_response = Mock(spec=Response)
        test_json_requests_response = {"test_response": "test_response"}
        test_requests_response.json.return_value = test_json_requests_response
        test_error_message = "test_error_message"
        test_json_rpc_error_response = Mock(spec=Error, message=test_error_message)
        to_result_mock.return_value = test_json_rpc_error_response
        requests_mock.post.return_value = test_requests_response

        with self.assertRaises(QueryExecutionFailed) as qef:
            self.json_rpc_query_bus.execute(test_query)

        self.assertEqual(test_query, qef.exception.query)
        self.assertEqual(test_error_message, qef.exception.reason)
        self.query_serializer_mock.serialize.assert_called_once_with(test_query)
        request_mock.assert_called_once_with(test_query.__class__.__name__, params=(test_serialized_query,))
        requests_mock.post.assert_called_once_with(test_query_handler_addr, json=test_json_rpc_request)
        to_result_mock.assert_called_once_with(test_json_requests_response)
