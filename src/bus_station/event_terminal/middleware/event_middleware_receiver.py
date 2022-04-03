from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware import EventMiddleware
from bus_station.passengers.reception.passenger_middleware_receiver import PassengerMiddlewareReceiver


class EventMiddlewareReceiver(PassengerMiddlewareReceiver[Event, EventConsumer, EventMiddleware]):
    def receive(self, passenger: Event, passenger_bus_stop: EventConsumer) -> None:
        middlewares = list(self._get_middlewares())
        for middleware in middlewares:
            middleware.before_consume(passenger, passenger_bus_stop)

        passenger_bus_stop.consume(passenger)

        for middleware in reversed(middlewares):
            middleware.after_consume(passenger, passenger_bus_stop)
