from abc import abstractmethod

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.passengers.passenger_middleware import PassengerMiddleware


class EventMiddleware(PassengerMiddleware):
    @abstractmethod
    def before_consume(self, passenger: Event, bus_stop: EventConsumer) -> None:
        pass

    @abstractmethod
    def after_consume(self, passenger: Event, bus_stop: EventConsumer) -> None:
        pass
