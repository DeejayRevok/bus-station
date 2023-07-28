from abc import abstractmethod
from typing import Any, Type

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_response import QueryResponse


class QueryHandler(BusStop):
    @abstractmethod
    def handle(self, query: Any) -> QueryResponse:
        pass

    @classmethod
    def bus_stop_name(cls) -> str:
        return f"query_handler.{cls.__module__}.{cls.__name__}"

    @classmethod
    def passenger(cls) -> Type[Query]:
        passenger = cls._get_passenger_from_handling_method(cls.handle, "query")
        return passenger
