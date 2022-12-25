from abc import abstractmethod

from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.shared_terminal.bus_stop import BusStop


class QueryHandler(BusStop):
    @abstractmethod
    def handle(self, query: Query) -> QueryResponse:
        pass

    @classmethod
    def bus_stop_name(cls) -> str:
        return f"query_handler.{cls.__module__}.{cls.__name__}"
