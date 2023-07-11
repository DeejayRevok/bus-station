from unittest import TestCase
from unittest.mock import Mock, patch

from jsonrpcserver.result import SuccessResult

from bus_station.bus_stop.registration.address.address_not_found_for_passenger import AddressNotFoundForPassenger
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus import JsonRPCQueryBus
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer


class TestJsonRPCQueryBus(TestCase):
    def setUp(self) -> None:
        self.address_registry_mock = Mock(spec=BusStopAddressRegistry)
        self.query_serializer_mock = Mock(spec=PassengerSerializer)
        self.query_response_deserializer_mock = Mock(spec=QueryResponseDeserializer)
        self.json_rpc_query_bus = JsonRPCQueryBus(
            self.query_serializer_mock,
            self.query_response_deserializer_mock,
            self.address_registry_mock,
        )

    def test_transport_passenger_address_not_found(self):
        test_query = Mock(spec=Query, **{"passenger_name.return_value": "test_query"})
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.return_value = None

        with self.assertRaises(AddressNotFoundForPassenger) as context:
            self.json_rpc_query_bus.transport(test_query)

        self.assertEqual("test_query", context.exception.passenger_name)
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.assert_called_once_with(
            test_query.__class__
        )

    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.request")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.parse")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.requests")
    def test_transport_success(self, requests_mock, parse_mock, request_mock):
        test_query = Mock(spec=Query, **{"passenger_name.return_value": "test_query"})
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.return_value = "test_address"
        self.query_serializer_mock.serialize.return_value = "test_query_serialized"
        requests_response = Mock(**{"json.return_value": "test_query_response"})
        requests_mock.post.return_value = requests_response
        test_query_response = Mock(spec=QueryResponse)
        self.query_response_deserializer_mock.deserialize.return_value = test_query_response
        test_json_rpc_response = Mock(spec=SuccessResult)
        parse_mock.return_value = test_json_rpc_response
        request_mock.return_value = {"test_request": "test_request_value"}

        result = self.json_rpc_query_bus.transport(test_query)

        self.assertEqual(test_query_response, result)
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.assert_called_once_with(
            test_query.__class__
        )
        self.query_serializer_mock.serialize.assert_called_once_with(test_query)
        self.query_response_deserializer_mock.deserialize.assert_called_once_with(test_json_rpc_response.result)
        parse_mock.assert_called_once_with("test_query_response")
        requests_mock.post.assert_called_once_with("test_address", json={"test_request": "test_request_value"})
