from typing import Type

from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.serialization.query_response_serializer import QueryResponseSerializer
from bus_station.shared_terminal.rpyc_service import RPyCService


class RPyCQueryService(RPyCService[Query, QueryHandler]):
    def __init__(
        self,
        query_deserializer: PassengerDeserializer,
        query_response_serializer: QueryResponseSerializer,
        query_receiver: PassengerReceiver[Query, QueryHandler],
    ):
        RPyCService.__init__(self, query_deserializer, query_receiver)
        self.__query_response_serializer = query_response_serializer

    def passenger_receiver(
        self, bus_stop: QueryHandler, passenger_class: Type[Query], serialized_passenger: str
    ) -> str:
        query = self._passenger_deserializer.deserialize(serialized_passenger, passenger_cls=passenger_class)
        if not isinstance(query, Query):
            raise TypeError("Input serialized query is not a Query")
        query_response = self._passenger_receiver.receive(query, bus_stop)
        return self.__query_response_serializer.serialize(query_response)
