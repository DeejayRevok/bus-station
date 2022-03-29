from abc import ABC, abstractmethod
from typing import Optional, Type

from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.registry.query_registry import QueryRegistry


class RemoteQueryRegistry(QueryRegistry, ABC):
    @abstractmethod
    def _register(self, query: Type[Query], handler: QueryHandler, handler_contact: str) -> None:
        pass

    @abstractmethod
    def get_query_destination_contact(self, query: Type[Query]) -> Optional[str]:
        pass
