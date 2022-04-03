from abc import abstractmethod

from bus_station.passengers.passenger_middleware import PassengerMiddleware
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse


class QueryMiddleware(PassengerMiddleware):
    @abstractmethod
    def before_handle(self, passenger: Query, bus_stop: QueryHandler) -> None:
        pass

    @abstractmethod
    def after_handle(self, passenger: Query, bus_stop: QueryHandler, query_response: QueryResponse) -> QueryResponse:
        pass
