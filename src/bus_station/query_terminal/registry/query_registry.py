from abc import ABCMeta, abstractmethod
from typing import Any, Iterable, Optional, Type, get_type_hints

from bus_station.query_terminal.handler_for_query_already_registered import HandlerForQueryAlreadyRegistered
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler


class QueryRegistry(metaclass=ABCMeta):
    def register(self, handler: QueryHandler, handler_contact: Any) -> None:
        handler_query = self.__get_handler_query(handler)
        self.__check_query_already_registered(handler_query)
        self._register(handler_query, handler, handler_contact)

    def __check_query_already_registered(self, query: Type[Query]) -> None:
        if self.get_query_destination_contact(query) is not None:
            raise HandlerForQueryAlreadyRegistered(query.__name__)

    def __get_handler_query(self, handler: QueryHandler) -> Type[Query]:
        handle_typing = get_type_hints(handler.handle)

        if "query" not in handle_typing:
            raise TypeError(f"Handle query not found for {handler.__class__.__name__}")

        if not issubclass(handle_typing["query"], Query):
            raise TypeError(f"Wrong type for handle query of {handler.__class__.__name__}")

        return handle_typing["query"]

    @abstractmethod
    def _register(self, query: Type[Query], handler: QueryHandler, handler_contact: Any) -> None:
        pass

    @abstractmethod
    def get_query_destination(self, query: Type[Query]) -> Optional[QueryHandler]:
        pass

    @abstractmethod
    def get_query_destination_contact(self, query: Type[Query]) -> Optional[Any]:
        pass

    @abstractmethod
    def get_queries_registered(self) -> Iterable[Type[Query]]:
        pass

    @abstractmethod
    def unregister(self, query: Type[Query]) -> None:
        pass
