from abc import abstractmethod

from bus_station.event_terminal.event import Event
from bus_station.shared_terminal.bus import Bus


class EventBus(Bus[Event]):
    @abstractmethod
    def _transport(self, passenger: Event) -> None:
        pass
