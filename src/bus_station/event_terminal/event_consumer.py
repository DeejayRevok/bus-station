from abc import abstractmethod
from typing import Any, Type

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.event_terminal.event import Event


class EventConsumer(BusStop):
    @abstractmethod
    def consume(self, event: Any) -> None:
        pass

    @classmethod
    def bus_stop_name(cls) -> str:
        return f"event_consumer.{cls.__module__}.{cls.__name__}"

    @classmethod
    def passenger(cls) -> Type[Event]:
        passenger = cls._get_passenger_from_handling_method(cls.consume, "event")
        return passenger
