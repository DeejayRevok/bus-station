from abc import abstractmethod

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.shared_terminal.bus import Bus


class EventBus(Bus[Event]):
    def __init__(self, event_receiver: PassengerReceiver[Event, EventConsumer]):
        self._event_receiver = event_receiver

    @abstractmethod
    def transport(self, passenger: Event) -> None:
        pass
