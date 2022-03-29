from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware import EventMiddleware
from bus_station.tracking_terminal.trackers.passenger_tracker import PassengerTracker


class TrackingEventMiddleware(EventMiddleware):
    def __init__(self, passenger_tracker: PassengerTracker):
        self.__tracker = passenger_tracker

    def before_consume(self, passenger: Event, bus_stop: EventConsumer) -> None:
        self.__tracker.start_tracking(passenger, bus_stop)

    def after_consume(self, passenger: Event, bus_stop: EventConsumer) -> None:
        self.__tracker.end_tracking(passenger)
