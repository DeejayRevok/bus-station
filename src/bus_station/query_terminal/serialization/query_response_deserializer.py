from abc import abstractmethod
from typing import Protocol

from bus_station.query_terminal.query_response import QueryResponse


class QueryResponseDeserializer(Protocol):
    @abstractmethod
    def deserialize(self, query_response_serialized: str) -> QueryResponse:
        pass
