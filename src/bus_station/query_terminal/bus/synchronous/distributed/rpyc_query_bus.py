from rpyc import Connection, connect

from bus_station.bus_stop.registration.address.address_not_found_for_bus_stop import AddressNotFoundForBusStop
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.passengers.passenger_registry import passenger_bus_stop_registry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.query_bus import QueryBus
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
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
        query_handler_ids = passenger_bus_stop_registry.get_bus_stops_for_passenger(passenger.passenger_name())
        if len(query_handler_ids) == 0:
            raise HandlerNotFoundForQuery(passenger.passenger_name())

        query_handler_id = next(iter(query_handler_ids))
        handler_address = self.__address_registry.get_bus_stop_address(query_handler_id)
        if handler_address is None:
            raise AddressNotFoundForBusStop(query_handler_id)

        return handler_address

    def __get_rpyc_client(self, handler_addr: str) -> Connection:
        host, port = handler_addr.split(":")
        return connect(host, port=port)

    def __execute_query(self, client: Connection, query: Query) -> QueryResponse:
        serialized_query = self.__query_serializer.serialize(query)
        serialized_query_response = getattr(client.root, query.passenger_name())(serialized_query)
        return self.__query_response_deserializer.deserialize(serialized_query_response)
