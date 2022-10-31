from typing import Any, List, Optional, Set, Type

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.event_registry import EventRegistry
from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.passengers.passenger_record.passenger_record import PassengerRecord
from bus_station.shared_terminal.bus_stop_resolver.bus_stop_resolver import BusStopResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter


class InMemoryEventRegistry(EventRegistry):
    def __init__(
        self,
        in_memory_repository: InMemoryPassengerRecordRepository,
        fqn_getter: FQNGetter,
        event_consumer_resolver: BusStopResolver[EventConsumer],
        passenger_class_resolver: PassengerClassResolver,
    ):
        self.__in_memory_repository = in_memory_repository
        self.__fqn_getter = fqn_getter
        self.__event_consumer_resolver = event_consumer_resolver
        self.__passenger_class_resolver = passenger_class_resolver

    def _register(self, event: Type[Event], consumer: EventConsumer, consumer_contact: Any) -> None:
        self.__in_memory_repository.save(
            PassengerRecord(
                passenger_name=event.__name__,
                passenger_fqn=self.__fqn_getter.get(event),
                destination_fqn=self.__fqn_getter.get(consumer),
                destination_contact=consumer_contact,
            )
        )

    def get_event_destinations(self, event: Type[Event]) -> Optional[Set[EventConsumer]]:
        event_records: Optional[List[PassengerRecord[Any]]] = self.__in_memory_repository.find_by_passenger_name(
            event.__name__
        )
        if event_records is None:
            return None

        event_destinations = set()
        for event_record in event_records:
            if event_record.destination_fqn is None:
                continue
            event_destinations.add(self.__event_consumer_resolver.resolve_from_fqn(event_record.destination_fqn))
        return event_destinations

    def get_event_destination_contact(self, event_destination: EventConsumer) -> Optional[Any]:
        event = self.get_consumer_event(event_destination)
        event_record = self.__in_memory_repository.find_by_passenger_name_and_destination(
            passenger_name=event.__name__, passenger_destination_fqn=self.__fqn_getter.get(event_destination)
        )
        if event_record is None:
            return None

        return event_record.destination_contact

    def get_event_destination_contacts(self, event: Type[Event]) -> Optional[Set[Any]]:
        event_records: Optional[List[PassengerRecord[Any]]] = self.__in_memory_repository.find_by_passenger_name(
            event.__name__
        )
        if event_records is None:
            return None

        event_destination_contacts = set()
        for event_record in event_records:
            if event_record.destination_contact in event_destination_contacts:
                continue
            event_destination_contacts.add(event_record.destination_contact)
        return event_destination_contacts

    def get_events_registered(self) -> Set[Type[Event]]:
        events_registered = set()
        for event_record in self.__in_memory_repository.all():
            event = self.__passenger_class_resolver.resolve_from_fqn(event_record.passenger_fqn)
            if event is None or not issubclass(event, Event):
                continue
            events_registered.add(event)
        return events_registered

    def unregister(self, event: Type[Event]) -> None:
        self.__in_memory_repository.delete_by_passenger_name(event.__name__)
