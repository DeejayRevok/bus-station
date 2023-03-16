from bus_station.passengers.reception.passenger_middleware_receiver import PassengerMiddlewareReceiver
from bus_station.query_terminal.middleware.query_middleware import QueryMiddleware
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse


class QueryMiddlewareReceiver(PassengerMiddlewareReceiver[Query, QueryHandler, QueryMiddleware]):
    def _receive(self, passenger: Query, passenger_bus_stop: QueryHandler) -> QueryResponse:
        middlewares = list(self._get_middlewares())
        for middleware in middlewares:
            middleware.before_handle(passenger, passenger_bus_stop)

        query_response = QueryResponse(data=None)
        handling_exception = None
        try:
            query_response = passenger_bus_stop.handle(passenger)
        except Exception as ex:
            handling_exception = ex

        for middleware in reversed(middlewares):
            query_response = middleware.after_handle(
                passenger, passenger_bus_stop, query_response, handling_exception=handling_exception
            )

        if handling_exception is not None:
            raise handling_exception

        return query_response
