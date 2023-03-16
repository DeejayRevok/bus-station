from abc import abstractmethod

from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.shared_terminal.bus import Bus


class QueryBus(Bus[Query]):
    @abstractmethod
    def _transport(self, passenger: Query) -> QueryResponse:
        pass
