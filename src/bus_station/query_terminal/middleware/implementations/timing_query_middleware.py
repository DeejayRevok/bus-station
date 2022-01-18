import time
from logging import Logger

from bus_station.query_terminal.middleware.query_middleware import QueryMiddleware
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse


class TimingQueryMiddleware(QueryMiddleware):
    def __init__(self, logger: Logger):
        self.__logger = logger
        self.__start_time = None

    def before_handle(self, passenger: Query, bus_stop: QueryHandler) -> None:
        self.__start_time = time.time()

    def after_handle(self, passenger: Query, bus_stop: QueryHandler, query_response: QueryResponse) -> QueryResponse:
        execution_time = time.time() - self.__start_time
        self.__logger.info(f"Query {passenger} handled by {bus_stop.__class__.__name__} in {execution_time} seconds")
        return query_response
