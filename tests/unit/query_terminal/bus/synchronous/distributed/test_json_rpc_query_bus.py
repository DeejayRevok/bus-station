from unittest import TestCase
from unittest.mock import Mock, patch

from jsonrpcclient import Error
from jsonrpcserver import Success
from requests import Response

from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus import JsonRPCQueryBus
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_execution_failed import QueryExecutionFailed
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.remote_query_registry import RemoteQueryRegistry
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer


class TestJsonRPCQueryBus(TestCase):
    def setUp(self) -> None:
        self.query_serializer_mock = Mock(spec=PassengerSerializer)
        self.query_response_deserializer_mock = Mock(spec=QueryResponseDeserializer)
        self.query_registry_mock = Mock(spec=RemoteQueryRegistry)
        self.json_rpc_query_bus = JsonRPCQueryBus(
            self.query_serializer_mock,
            self.query_response_deserializer_mock,
            self.query_registry_mock,
        )

    @patch("bus_station.shared_terminal.bus.get_distributed_id")
    def test_transport_not_registered(self, get_distributed_id_mock):
        get_distributed_id_mock.return_value = "test_distributed_id"
        test_query = Mock(spec=Query, **{"passenger_name.return_value": "test_query"})
        self.query_registry_mock.get_query_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForQuery) as hnffq:
            self.json_rpc_query_bus.transport(test_query)

        self.assertEqual("test_query", hnffq.exception.query_name)
        self.query_serializer_mock.serialize.assert_not_called()
        self.query_registry_mock.get_query_destination_contact.assert_called_once_with("test_query")
        test_query.set_distributed_id.assert_called_once_with("test_distributed_id")

    @patch("bus_station.shared_terminal.bus.get_distributed_id")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.parse")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.request")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.requests")
    def test_transport_success(self, requests_mock, request_mock, to_result_mock, get_distributed_id_mock):
        get_distributed_id_mock.return_value = "test_distributed_id"
        test_query = Mock(spec=Query, **{"passenger_name.return_value": "test_query"})
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

        query_response = self.json_rpc_query_bus.transport(test_query)

        self.assertEqual(test_query_response, query_response)
        self.query_serializer_mock.serialize.assert_called_once_with(test_query)
        request_mock.assert_called_once_with(test_query.passenger_name(), params=(test_serialized_query,))
        requests_mock.post.assert_called_once_with(test_query_handler_addr, json=test_json_rpc_request)
        to_result_mock.assert_called_once_with(test_json_requests_response)
        self.query_response_deserializer_mock.deserialize.assert_called_once_with(test_query_response_serialized)
        test_query.set_distributed_id.assert_called_once_with("test_distributed_id")

    @patch("bus_station.shared_terminal.bus.get_distributed_id")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.parse")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.request")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.requests")
    def test_transport_error(self, requests_mock, request_mock, to_result_mock, get_distributed_id_mock):
        get_distributed_id_mock.return_value = "test_distributed_id"
        test_query = Mock(spec=Query, **{"passenger_name.return_value": "test_query"})
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
            self.json_rpc_query_bus.transport(test_query)

        self.assertEqual(test_query, qef.exception.query)
        self.assertEqual(test_error_message, qef.exception.reason)
        self.query_serializer_mock.serialize.assert_called_once_with(test_query)
        request_mock.assert_called_once_with(test_query.passenger_name(), params=(test_serialized_query,))
        requests_mock.post.assert_called_once_with(test_query_handler_addr, json=test_json_rpc_request)
        to_result_mock.assert_called_once_with(test_json_requests_response)
        test_query.set_distributed_id.assert_called_once_with("test_distributed_id")
