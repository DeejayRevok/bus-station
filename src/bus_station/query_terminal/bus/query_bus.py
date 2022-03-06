from abc import abstractmethod

from bus_station.query_terminal.middleware.query_middleware import QueryMiddleware
from bus_station.query_terminal.middleware.query_middleware_executor import QueryMiddlewareExecutor
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.shared_terminal.bus import Bus


class QueryBus(Bus[QueryMiddleware]):
    def __init__(self):
        super().__init__(QueryMiddlewareExecutor)

    @abstractmethod
    def execute(self, query: Query) -> QueryResponse:
        pass
