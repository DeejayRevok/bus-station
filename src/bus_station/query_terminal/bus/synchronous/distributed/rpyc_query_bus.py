from rpyc import Connection, connect

from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.query_bus import QueryBus
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.remote_query_registry import RemoteQueryRegistry
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer


class RPyCQueryBus(QueryBus):
    def __init__(
        self,
        query_serializer: PassengerSerializer,
        query_response_deserializer: QueryResponseDeserializer,
        query_registry: RemoteQueryRegistry,
    ):
        self.__query_serializer = query_serializer
        self.__query_response_deserializer = query_response_deserializer
        self.__query_registry = query_registry

    def transport(self, passenger: Query) -> QueryResponse:
        query_handler_addr = self.__query_registry.get_query_destination_contact(passenger.__class__)
        if query_handler_addr is None:
            raise HandlerNotFoundForQuery(passenger.__class__.__name__)

        rpyc_client = self.__get_rpyc_client(query_handler_addr)
        query_response = self.__execute_query(rpyc_client, passenger)
        rpyc_client.close()
        return query_response

    def __get_rpyc_client(self, handler_addr: str) -> Connection:
        host, port = handler_addr.split(":")
        return connect(host, port=port)

    def __execute_query(self, client: Connection, query: Query) -> QueryResponse:
        serialized_query = self.__query_serializer.serialize(query)
        serialized_query_response = getattr(client.root, query.__class__.__name__)(serialized_query)
        return self.__query_response_deserializer.deserialize(serialized_query_response)
