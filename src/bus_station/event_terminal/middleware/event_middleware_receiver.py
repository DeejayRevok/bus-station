from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware import EventMiddleware
from bus_station.passengers.reception.passenger_middleware_receiver import PassengerMiddlewareReceiver


class EventMiddlewareReceiver(PassengerMiddlewareReceiver[Event, EventConsumer, EventMiddleware]):
    def _receive(self, passenger: Event, passenger_bus_stop: EventConsumer) -> None:
        middlewares = list(self._get_middlewares())
        for middleware in middlewares:
            middleware.before_consume(passenger, passenger_bus_stop)

        consume_exception = None
        try:
            passenger_bus_stop.consume(passenger)
        except Exception as ex:
            consume_exception = ex

        for middleware in reversed(middlewares):
            middleware.after_consume(passenger, passenger_bus_stop, consume_exception=consume_exception)

        if consume_exception is not None:
            raise consume_exception
