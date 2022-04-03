from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.query_terminal.bus.query_bus import QueryBus
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.in_memory_query_registry import InMemoryQueryRegistry


class SyncQueryBus(QueryBus):
    def __init__(self, query_registry: InMemoryQueryRegistry, query_receiver: PassengerReceiver[Query, QueryHandler]):
        super().__init__(query_receiver)
        self.__query_registry = query_registry

    def transport(self, passenger: Query) -> QueryResponse:
        query_handler = self.__query_registry.get_query_destination_contact(passenger.__class__)
        if query_handler is None:
            raise HandlerNotFoundForQuery(passenger.__class__.__name__)
        return self._query_receiver.receive(passenger, query_handler)
