import requests
from jsonrpcclient import request
from jsonrpcclient.responses import Error, to_result

from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.query_bus import QueryBus
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_execution_failed import QueryExecutionFailed
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.remote_query_registry import RemoteQueryRegistry
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer


class JsonRPCQueryBus(QueryBus):
    def __init__(
        self,
        query_serializer: PassengerSerializer,
        query_response_deserializer: QueryResponseDeserializer,
        query_registry: RemoteQueryRegistry,
    ):
        self.__query_serializer = query_serializer
        self.__query_registry = query_registry
        self.__query_response_deserializer = query_response_deserializer

    def transport(self, passenger: Query) -> QueryResponse:
        handler_address = self.__query_registry.get_query_destination_contact(passenger.__class__)
        if handler_address is None:
            raise HandlerNotFoundForQuery(passenger.__class__.__name__)

        return self.__execute_query(passenger, handler_address)

    def __execute_query(self, query: Query, query_handler_addr: str) -> QueryResponse:
        serialized_query = self.__query_serializer.serialize(query)

        request_response = requests.post(
            query_handler_addr, json=request(query.__class__.__name__, params=(serialized_query,))
        )
        json_rpc_response = to_result(request_response.json())

        if isinstance(json_rpc_response, Error):
            raise QueryExecutionFailed(query, json_rpc_response.message)
        return self.__query_response_deserializer.deserialize(json_rpc_response.result)
