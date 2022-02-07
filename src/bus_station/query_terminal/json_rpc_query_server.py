from typing import Type

from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.serialization.query_response_serializer import QueryResponseSerializer
from bus_station.shared_terminal.json_rpc_server import JsonRPCServer


class JsonRPCQueryServer(JsonRPCServer[Query, QueryHandler]):
    def __init__(
        self,
        passenger_deserializer: PassengerDeserializer,
        passenger_middleware_executor: PassengerMiddlewareExecutor,
        query_response_serializer: QueryResponseSerializer,
    ):
        JsonRPCServer.__init__(self, passenger_deserializer, passenger_middleware_executor)
        self.__query_response_serializer = query_response_serializer

    def _passenger_executor(
        self, bus_stop: QueryHandler, passenger_class: Type[Query], serialized_passenger: str
    ) -> str:
        query = self._passenger_deserializer.deserialize(serialized_passenger, passenger_cls=passenger_class)
        if not isinstance(query, Query):
            raise TypeError("Input serialized query is not a Query")
        query_response = self._passenger_middleware_executor.execute(query, bus_stop)
        return self.__query_response_serializer.serialize(query_response)
