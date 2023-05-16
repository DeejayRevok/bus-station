from unittest import TestCase
from unittest.mock import Mock, patch

from jsonrpcserver.result import SuccessResult

from bus_station.bus_stop.registration.address.address_not_found_for_bus_stop import AddressNotFoundForBusStop
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus import JsonRPCQueryBus
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
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

    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.passenger_bus_stop_registry")
    def test_transport_query_not_registered(self, passenger_bus_stop_registry_mock):
        test_query = Mock(spec=Query, **{"passenger_name.return_value": "test_query"})
        passenger_bus_stop_registry_mock.get_bus_stops_for_passenger.return_value = set()

        with self.assertRaises(HandlerNotFoundForQuery) as context:
            self.json_rpc_query_bus.transport(test_query)

        self.assertEqual("test_query", context.exception.query_name)
        passenger_bus_stop_registry_mock.get_bus_stops_for_passenger.assert_called_once_with("test_query")

    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.passenger_bus_stop_registry")
    def test_transport_query_handler_address_not_found(self, passenger_bus_stop_registry_mock):
        test_query = Mock(spec=Query, **{"passenger_name.return_value": "test_query"})
        passenger_bus_stop_registry_mock.get_bus_stops_for_passenger.return_value = {"test_bus_stop"}
        self.address_registry_mock.get_bus_stop_address.return_value = None

        with self.assertRaises(AddressNotFoundForBusStop) as context:
            self.json_rpc_query_bus.transport(test_query)

        self.assertEqual("test_bus_stop", context.exception.bus_stop_id)
        passenger_bus_stop_registry_mock.get_bus_stops_for_passenger.assert_called_once_with("test_query")
        self.address_registry_mock.get_bus_stop_address.assert_called_once_with("test_bus_stop")

    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.request")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.parse")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.requests")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.json_rpc_query_bus.passenger_bus_stop_registry")
    def test_transport_success(self, passenger_bus_stop_registry_mock, requests_mock, parse_mock, request_mock):
        test_query = Mock(spec=Query, **{"passenger_name.return_value": "test_query"})
        passenger_bus_stop_registry_mock.get_bus_stops_for_passenger.return_value = {"test_bus_stop"}
        self.address_registry_mock.get_bus_stop_address.return_value = "test_address"
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
        passenger_bus_stop_registry_mock.get_bus_stops_for_passenger.assert_called_once_with("test_query")
        self.address_registry_mock.get_bus_stop_address.assert_called_once_with("test_bus_stop")
        self.query_serializer_mock.serialize.assert_called_once_with(test_query)
        self.query_response_deserializer_mock.deserialize.assert_called_once_with(test_json_rpc_response.result)
        parse_mock.assert_called_once_with("test_query_response")
        requests_mock.post.assert_called_once_with("test_address", json={"test_request": "test_request_value"})
