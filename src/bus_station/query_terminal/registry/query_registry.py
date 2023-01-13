from abc import ABCMeta, abstractmethod
from typing import Any, Iterable, Optional, Type

from bus_station.passengers.resolve_passenger_from_bus_stop import resolve_passenger_from_bus_stop
from bus_station.query_terminal.handler_for_query_already_registered import HandlerForQueryAlreadyRegistered
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler


class QueryRegistry(metaclass=ABCMeta):
    def register(self, handler: QueryHandler, handler_contact: Any) -> None:
        handler_query = resolve_passenger_from_bus_stop(handler, "handle", "query", Query)
        existing_handler_contact = self.get_query_destination_contact(handler_query.passenger_name())
        self.__check_query_already_registered(handler_query, handler_contact, existing_handler_contact)
        if existing_handler_contact is None:
            self._register(handler_query, handler, handler_contact)

    def __check_query_already_registered(
        self, query: Type[Query], handler_contact: Any, existing_handler_contact: Optional[Any]
    ) -> None:
        if existing_handler_contact is not None and handler_contact != existing_handler_contact:
            raise HandlerForQueryAlreadyRegistered(query.passenger_name())

    @abstractmethod
    def _register(self, query: Type[Query], handler: QueryHandler, handler_contact: Any) -> None:
        pass

    @abstractmethod
    def get_query_destination(self, query_name: str) -> Optional[QueryHandler]:
        pass

    @abstractmethod
    def get_query_destination_contact(self, query_name: str) -> Optional[Any]:
        pass

    @abstractmethod
    def get_queries_registered(self) -> Iterable[Type[Query]]:
        pass

    @abstractmethod
    def unregister(self, query_name: str) -> None:
        pass
