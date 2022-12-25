from abc import abstractmethod

from bus_station.event_terminal.event import Event
from bus_station.shared_terminal.bus_stop import BusStop


class EventConsumer(BusStop):
    @abstractmethod
    def consume(self, event: Event) -> None:
        pass

    @classmethod
    def bus_stop_name(cls) -> str:
        return f"event_consumer.{cls.__module__}.{cls.__name__}"
