from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor
from bus_station.query_terminal.middleware.query_middleware import QueryMiddleware
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse


class QueryMiddlewareExecutor(PassengerMiddlewareExecutor[Query, QueryMiddleware, QueryHandler]):
    def execute(self, passenger: Query, passenger_bus_stop: QueryHandler) -> QueryResponse:
        middlewares = list(self._get_middlewares())
        for middleware in middlewares:
            middleware.before_handle(passenger, passenger_bus_stop)

        query_response = passenger_bus_stop.handle(passenger)

        for middleware in reversed(middlewares):
            query_response = middleware.after_handle(passenger, passenger_bus_stop, query_response)

        return query_response
