from dataclasses import asdict

from bus_station.query_terminal.middleware.query_middleware import QueryMiddleware
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.tracking_terminal.trackers.passenger_tracker import PassengerTracker


class TrackingQueryMiddleware(QueryMiddleware):
    def __init__(self, passenger_tracker: PassengerTracker):
        self.__tracker = passenger_tracker

    def before_handle(self, passenger: Query, bus_stop: QueryHandler) -> None:
        self.__tracker.start_tracking(passenger, bus_stop)

    def after_handle(self, passenger: Query, bus_stop: QueryHandler, query_response: QueryResponse) -> QueryResponse:
        self.__tracker.end_tracking(passenger, response_data=asdict(query_response))
        return query_response
