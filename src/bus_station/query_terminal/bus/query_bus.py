from abc import abstractmethod

from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.shared_terminal.bus import Bus


class QueryBus(Bus[Query]):
    def __init__(self, query_receiver: PassengerReceiver[Query, QueryHandler]):
        self._query_receiver = query_receiver

    @abstractmethod
    def transport(self, passenger: Query) -> QueryResponse:
        pass
