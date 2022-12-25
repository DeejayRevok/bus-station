from logging import Logger
from typing import Optional

from bus_station.query_terminal.middleware.query_middleware import QueryMiddleware
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse


class LoggingQueryMiddleware(QueryMiddleware):
    def __init__(self, logger: Logger):
        self.__logger = logger

    def before_handle(self, passenger: Query, bus_stop: QueryHandler) -> None:
        self.__logger.info(f"Starting handling query {passenger} with {bus_stop.bus_stop_name()}")

    def after_handle(
        self,
        passenger: Query,
        bus_stop: QueryHandler,
        query_response: QueryResponse,
        handling_exception: Optional[Exception] = None,
    ) -> QueryResponse:
        if handling_exception is not None:
            self.__logger.exception(
                handling_exception,
                exc_info=(handling_exception.__class__, handling_exception, handling_exception.__traceback__),
            )
        self.__logger.info(
            f"Finished handling query {passenger} with {bus_stop.bus_stop_name()} with response: {query_response}"
        )
        return query_response
