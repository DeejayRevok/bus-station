from typing import Callable
from unittest import TestCase
from unittest.mock import Mock, patch

from rpyc import Connection

from bus_station.bus_stop.registration.address.address_not_found_for_passenger import AddressNotFoundForPassenger
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.synchronous.distributed.rpyc_query_bus import RPyCQueryBus
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer


class TestRPyCQueryBus(TestCase):
    def setUp(self) -> None:
        self.query_serializer_mock = Mock(spec=PassengerSerializer)
        self.query_response_deserializer_mock = Mock(spec=QueryResponseDeserializer)
        self.address_registry_mock = Mock(spec=BusStopAddressRegistry)
        self.rpyc_query_bus = RPyCQueryBus(
            self.query_serializer_mock,
            self.query_response_deserializer_mock,
            self.address_registry_mock,
        )

    def test_transport_passenger_address_not_found(self):
        test_query = Mock(spec=Query, **{"passenger_name.return_value": "test_query"})
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.return_value = None

        with self.assertRaises(AddressNotFoundForPassenger) as context:
            self.rpyc_query_bus.transport(test_query)

        self.assertEqual("test_query", context.exception.passenger_name)
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.assert_called_once_with(
            test_query.__class__
        )

    @patch("bus_station.query_terminal.bus.synchronous.distributed.rpyc_query_bus.connect")
    def test_transport_success(self, connect_mock):
        test_query = Mock(spec=Query, **{"passenger_name.return_value": "test_query"})
        test_query.passenger_name.return_value = "TestQuery"
        test_host = "test_host"
        test_port = "41124"
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.return_value = f"{test_host}:{test_port}"
        test_rpyc_connection = Mock(spec=Connection)
        connect_mock.return_value = test_rpyc_connection
        test_serialized_query = "test_serialized_query"
        self.query_serializer_mock.serialize.return_value = test_serialized_query
        test_rpyc_callable = Mock(spec=Callable)
        setattr(test_rpyc_connection.root, test_query.passenger_name(), test_rpyc_callable)
        test_query_response = Mock(spec=QueryResponse)
        test_serialized_query_response = "test_serialized_query_response"
        test_rpyc_callable.return_value = test_serialized_query_response
        self.query_response_deserializer_mock.deserialize.return_value = test_query_response

        query_response = self.rpyc_query_bus.transport(test_query)

        self.assertEqual(test_query_response, query_response)
        connect_mock.assert_called_once_with(test_host, port=test_port)
        self.query_serializer_mock.serialize.assert_called_once_with(test_query)
        test_rpyc_callable.assert_called_once_with(test_serialized_query)
        self.query_response_deserializer_mock.deserialize.assert_called_once_with(test_serialized_query_response)
        test_rpyc_connection.close.assert_called_once_with()
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.assert_called_once_with(
            test_query.__class__
        )
