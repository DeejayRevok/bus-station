from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.query_terminal.bus.query_bus import QueryBus
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_handler_registry import QueryHandlerRegistry
from bus_station.query_terminal.query_response import QueryResponse


class SyncQueryBus(QueryBus):
    def __init__(
        self, query_handler_registry: QueryHandlerRegistry, query_receiver: PassengerReceiver[Query, QueryHandler]
    ):
        self.__query_receiver = query_receiver
        self.__query_handler_registry = query_handler_registry

    def _transport(self, passenger: Query) -> QueryResponse:
        query_handler = self.__query_handler_registry.get_handler_from_query(passenger.passenger_name())
        if query_handler is None:
            raise HandlerNotFoundForQuery(passenger.passenger_name())
        return self.__query_receiver.receive(passenger, query_handler)
