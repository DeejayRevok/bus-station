from abc import abstractmethod
from typing import get_type_hints, Type

from bus_station.query_terminal.middleware.query_middleware import QueryMiddleware
from bus_station.query_terminal.middleware.query_middleware_executor import QueryMiddlewareExecutor
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.shared_terminal.bus import Bus
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_response import QueryResponse


class QueryBus(Bus[QueryHandler, QueryMiddleware]):
    def __init__(self):
        super().__init__(QueryMiddlewareExecutor)

    def _get_handler_query(self, handler: QueryHandler) -> Type[Query]:
        handle_typing = get_type_hints(handler.handle)

        if "query" not in handle_typing:
            raise TypeError(f"Handle query not found for {handler.__class__.__name__}")

        if not issubclass(handle_typing["query"], Query):
            raise TypeError(f"Wrong type for handle query of {handler.__class__.__name__}")

        return handle_typing["query"]

    @abstractmethod
    def execute(self, query: Query) -> QueryResponse:
        pass
