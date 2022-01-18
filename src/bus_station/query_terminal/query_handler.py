from abc import abstractmethod

from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.shared_terminal.bus_stop import BusStop


class QueryHandler(BusStop):
    @abstractmethod
    def handle(self, query: Query) -> QueryResponse:
        pass
