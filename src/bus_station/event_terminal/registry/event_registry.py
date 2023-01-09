from abc import ABCMeta, abstractmethod
from typing import Any, Iterable, Optional, Type, get_type_hints

from bus_station.event_terminal.consumer_for_event_already_registered import ConsumerForEventAlreadyRegistered
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer


class EventRegistry(metaclass=ABCMeta):
    def register(self, consumer: EventConsumer, consumer_contact: Any) -> None:
        consumer_event = self.get_consumer_event(consumer)
        existing_event_destination_contact = self.get_event_destination_contact(consumer)

        if existing_event_destination_contact is None:
            self._register(consumer_event, consumer, consumer_contact)
            return

        if existing_event_destination_contact != consumer_contact:
            raise ConsumerForEventAlreadyRegistered(consumer.bus_stop_name(), consumer_event.passenger_name())

    def get_consumer_event(self, consumer: EventConsumer) -> Type[Event]:
        consumer_typing = get_type_hints(consumer.consume)

        if "event" not in consumer_typing:
            raise TypeError(f"Consumer event not found for {consumer.bus_stop_name()}")

        if not issubclass(consumer_typing["event"], Event):
            raise TypeError(f"Wrong type for consume event of {consumer.bus_stop_name()}")

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
    def get_event_destination_contact(self, event_destination: EventConsumer) -> Optional[Any]:
        pass

    @abstractmethod
    def get_events_registered(self) -> Iterable[Type[Event]]:
        pass

    @abstractmethod
    def unregister(self, event: Type[Event]) -> None:
        pass
