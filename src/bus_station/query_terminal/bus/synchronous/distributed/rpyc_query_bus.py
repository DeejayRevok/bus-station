from rpyc import Connection, connect

from bus_station.bus_stop.registration.address.address_not_found_for_passenger import AddressNotFoundForPassenger
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.query_bus import QueryBus
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer


class RPyCQueryBus(QueryBus):
    def __init__(
        self,
        query_serializer: PassengerSerializer,
        query_response_deserializer: QueryResponseDeserializer,
        address_registry: BusStopAddressRegistry,
    ):
        self.__query_serializer = query_serializer
        self.__query_response_deserializer = query_response_deserializer
        self.__address_registry = address_registry

    def _transport(self, passenger: Query) -> QueryResponse:
        handler_address = self.__get_handler_address(passenger)

        rpyc_client = self.__get_rpyc_client(handler_address)
        query_response = self.__execute_query(rpyc_client, passenger)
        rpyc_client.close()
        return query_response

    def __get_handler_address(self, passenger: Query) -> str:
        handler_address = self.__address_registry.get_address_for_bus_stop_passenger_class(passenger.__class__)
        if handler_address is None:
            raise AddressNotFoundForPassenger(passenger.passenger_name())

        return handler_address

    def __get_rpyc_client(self, handler_addr: str) -> Connection:
        host, port = handler_addr.split(":")
        return connect(host, port=port)

    def __execute_query(self, client: Connection, query: Query) -> QueryResponse:
        serialized_query = self.__query_serializer.serialize(query)
        serialized_query_response = getattr(client.root, query.passenger_name())(serialized_query)
        return self.__query_response_deserializer.deserialize(serialized_query_response)
