from abc import ABCMeta, abstractmethod
from typing import Any, Iterable, Optional, Type

from bus_station.event_terminal.consumer_for_event_already_registered import ConsumerForEventAlreadyRegistered
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.passengers.resolve_passenger_from_bus_stop import resolve_passenger_from_bus_stop


class EventRegistry(metaclass=ABCMeta):
    def register(self, consumer: EventConsumer, consumer_contact: Any) -> None:
        consumer_event = resolve_passenger_from_bus_stop(consumer, "consume", "event", Event)
        existing_event_destination_contact = self.get_event_destination_contact(
            consumer_event.passenger_name(), consumer.bus_stop_name()
        )

        if existing_event_destination_contact is None:
            self._register(consumer_event, consumer, consumer_contact)
            return

        if existing_event_destination_contact != consumer_contact:
            raise ConsumerForEventAlreadyRegistered(consumer.bus_stop_name(), consumer_event.passenger_name())

    @abstractmethod
    def _register(self, event: Type[Event], consumer: EventConsumer, consumer_contact: Any) -> None:
        pass

    @abstractmethod
    def get_event_destinations(self, event_name: str) -> Optional[Iterable[EventConsumer]]:
        pass

    @abstractmethod
    def get_event_destination(self, event_name: str, event_destination_name: str) -> Optional[EventConsumer]:
        pass

    @abstractmethod
    def get_event_destination_contacts(self, event_name: str) -> Optional[Iterable[Any]]:
        pass

    @abstractmethod
    def get_event_destination_contact(self, event_name: str, event_destination_name: str) -> Optional[Any]:
        pass

    @abstractmethod
    def get_events_registered(self) -> Iterable[Type[Event]]:
        pass

    @abstractmethod
    def unregister(self, event_name: str) -> None:
        pass
