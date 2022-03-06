from abc import ABC, abstractmethod
from typing import Iterable, Optional, Tuple, Type

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.event_registry import EventRegistry


class RemoteEventRegistry(EventRegistry, ABC):
    @abstractmethod
    def _register(self, event: Type[Event], consumer: EventConsumer, consumer_contact: str) -> None:
        pass

    @abstractmethod
    def get_event_destination_contacts(self, event: Type[Event]) -> Optional[Iterable[str]]:
        pass

    @abstractmethod
    def get_events_registered(self) -> Iterable[Tuple[Type[Event], Iterable[EventConsumer], Iterable[str]]]:
        pass
