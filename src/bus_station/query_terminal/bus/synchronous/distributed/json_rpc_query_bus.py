import requests
from jsonrpcclient import Error, parse, request

from bus_station.bus_stop.registration.address.address_not_found_for_passenger import AddressNotFoundForPassenger
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.query_bus import QueryBus
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_execution_failed import QueryExecutionFailed
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer


class JsonRPCQueryBus(QueryBus):
    def __init__(
        self,
        query_serializer: PassengerSerializer,
        query_response_deserializer: QueryResponseDeserializer,
        address_registry: BusStopAddressRegistry,
    ):
        self.__query_serializer = query_serializer
        self.__address_registry = address_registry
        self.__query_response_deserializer = query_response_deserializer

    def _transport(self, passenger: Query) -> QueryResponse:
        handler_address = self.__get_handler_address(passenger)
        return self.__execute_query(passenger, handler_address)

    def __get_handler_address(self, passenger: Query) -> str:
        handler_address = self.__address_registry.get_address_for_bus_stop_passenger_class(passenger.__class__)
        if handler_address is None:
            raise AddressNotFoundForPassenger(passenger.passenger_name())

        return handler_address

    def __execute_query(self, query: Query, query_handler_addr: str) -> QueryResponse:
        serialized_query = self.__query_serializer.serialize(query)

        request_response = requests.post(
            query_handler_addr, json=request(query.passenger_name(), params=(serialized_query,))
        )
        json_rpc_response = parse(request_response.json())

        if isinstance(json_rpc_response, Error):
            raise QueryExecutionFailed(query, json_rpc_response.message)
        return self.__query_response_deserializer.deserialize(json_rpc_response.result)  # pyre-ignore [16]
