from abc import abstractmethod
from typing import Protocol

from bus_station.query_terminal.query_response import QueryResponse


class QueryResponseSerializer(Protocol):
    @abstractmethod
    def serialize(self, query_response: QueryResponse) -> str:
        pass
