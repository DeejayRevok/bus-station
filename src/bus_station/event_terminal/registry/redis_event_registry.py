from typing import List, Optional, Set, Type

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.remote_event_registry import RemoteEventRegistry
from bus_station.passengers.passenger_record.passenger_record import PassengerRecord
from bus_station.passengers.passenger_record.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.passengers.passenger_resolvers import resolve_passenger_class_from_fqn
from bus_station.shared_terminal.bus_stop_resolver.bus_stop_resolver import BusStopResolver
from bus_station.shared_terminal.fqn import resolve_fqn


class RedisEventRegistry(RemoteEventRegistry):
    def __init__(
        self,
        redis_repository: RedisPassengerRecordRepository,
        event_consumer_resolver: BusStopResolver[EventConsumer],
    ):
        self.__redis_repository = redis_repository
        self.__event_consumer_resolver = event_consumer_resolver

    def _register(self, event: Type[Event], consumer: EventConsumer, consumer_contact: str) -> None:
        self.__redis_repository.save(
            PassengerRecord(
                passenger_name=event.passenger_name(),
                passenger_fqn=resolve_fqn(event),
                destination_name=consumer.bus_stop_name(),
                destination_fqn=resolve_fqn(consumer),
                destination_contact=consumer_contact,
            )
        )

    def get_event_destination_contacts(self, event_name: str) -> Optional[Set[str]]:
        event_records = self.__redis_repository.find_by_passenger_name(event_name)
        if event_records is None:
            return None

        event_destination_contacts = set()
        for event_record in event_records:
            if event_record.destination_contact in event_destination_contacts:
                continue
            event_destination_contacts.add(event_record.destination_contact)
        return event_destination_contacts

    def get_event_destination_contact(self, event_name: str, event_destination_name: str) -> Optional[str]:
        event_record = self.__redis_repository.find_by_passenger_name_and_destination_name(
            passenger_name=event_name, passenger_destination_name=event_destination_name
        )
        if event_record is None:
            return None
        return event_record.destination_contact

    def get_events_registered(self) -> Set[Type[Event]]:
        events_registered = set()
        for event_record in self.__redis_repository.all():
            event = resolve_passenger_class_from_fqn(event_record.passenger_fqn)
            if event is None or not issubclass(event, Event):
                continue
            events_registered.add(event)
        return events_registered

    def get_event_destinations(self, event_name: str) -> Optional[Set[EventConsumer]]:
        event_records: Optional[List[PassengerRecord[str]]] = self.__redis_repository.find_by_passenger_name(event_name)
        if event_records is None:
            return None

        event_destinations = set()
        for event_record in event_records:
            event_destinations.add(self.__event_consumer_resolver.resolve_from_fqn(event_record.destination_fqn))
        return event_destinations

    def get_event_destination(self, event_name: str, event_destination_name: str) -> Optional[EventConsumer]:
        event_record: Optional[
            PassengerRecord[str]
        ] = self.__redis_repository.find_by_passenger_name_and_destination_name(event_name, event_destination_name)
        if event_record is None:
            return None

        return self.__event_consumer_resolver.resolve_from_fqn(event_record.destination_fqn)

    def unregister(self, event_name: str) -> None:
        self.__redis_repository.delete_by_passenger_name(event_name)
