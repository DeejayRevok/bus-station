from abc import ABCMeta, abstractmethod
from typing import Any, Iterable, Optional, Type, get_type_hints

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer


class EventRegistry(metaclass=ABCMeta):
    def register(self, consumer: EventConsumer, consumer_contact: Any) -> None:
        consumer_event = self.__get_consumer_event(consumer)
        self._register(consumer_event, consumer, consumer_contact)

    def __get_consumer_event(self, consumer: EventConsumer) -> Type[Event]:
        consumer_typing = get_type_hints(consumer.consume)

        if "event" not in consumer_typing:
            raise TypeError(f"Consumer event not found for {consumer.__class__.__name__}")

        if not issubclass(consumer_typing["event"], Event):
            raise TypeError(f"Wrong type for consume event of {consumer.__class__.__name__}")

        return consumer_typing["event"]

    @abstractmethod
    def _register(self, event: Type[Event], consumer: EventConsumer, consumer_contact: Any) -> None:
        pass

    @abstractmethod
    def get_event_destinations(self, event: Type[Event]) -> Optional[Iterable[EventConsumer]]:
        pass

    @abstractmethod
    def get_event_destination_contacts(self, event: Type[Event]) -> Optional[Iterable[Any]]:
        pass

    @abstractmethod
    def get_events_registered(self) -> Iterable[Type[Event]]:
        pass

    @abstractmethod
    def unregister(self, event: Type[Event]) -> None:
        pass
