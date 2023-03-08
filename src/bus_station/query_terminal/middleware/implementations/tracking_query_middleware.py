from dataclasses import asdict
from typing import Optional

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

    def after_handle(
        self,
        passenger: Query,
        bus_stop: QueryHandler,
        query_response: QueryResponse,
        handling_exception: Optional[Exception] = None,
    ) -> QueryResponse:
        success = handling_exception is None
        response_data = asdict(query_response) if query_response is not None else None
        self.__tracker.end_tracking(
            passenger=passenger, bus_stop=bus_stop, response_data=response_data, success=success
        )
        return query_response
