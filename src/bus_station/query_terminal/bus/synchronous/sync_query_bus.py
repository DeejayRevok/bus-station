from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry
from bus_station.query_terminal.bus.query_bus import QueryBus
from bus_station.query_terminal.handler_for_query_already_registered import HandlerForQueryAlreadyRegistered
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse


class SyncQueryBus(QueryBus):
    def __init__(self, query_registry: InMemoryRegistry):
        super().__init__()
        self.__query_registry = query_registry

    def register(self, handler: QueryHandler) -> None:
        handler_query = self._get_handler_query(handler)
        if handler_query in self.__query_registry:
            raise HandlerForQueryAlreadyRegistered(handler_query.__name__)
        self.__query_registry.register(handler_query, handler)

    def execute(self, query: Query) -> QueryResponse:
        query_handler = self.__query_registry.get_passenger_destination(query.__class__)
        if query_handler is None:
            raise HandlerNotFoundForQuery(query.__class__.__name__)
        return self._middleware_executor.execute(query, query_handler)
