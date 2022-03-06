from typing import Iterable, List, Optional, Tuple, Type

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.remote_event_registry import RemoteEventRegistry
from bus_station.passengers.registry.passenger_record import PassengerRecord
from bus_station.passengers.registry.redis_passenger_record_repository import RedisPassengerRecordRepository


class RedisEventRegistry(RemoteEventRegistry):
    def __init__(self, redis_repository: RedisPassengerRecordRepository):
        self.__redis_repository = redis_repository

    def _register(self, event: Type[Event], consumer: EventConsumer, consumer_contact: str) -> None:
        self.__redis_repository.save(
            PassengerRecord(passenger=event, destination=consumer, destination_contact=consumer_contact)
        )

    def get_event_destination_contacts(self, event: Type[Event]) -> Optional[Iterable[str]]:
        event_records = self.__redis_repository.filter_by_passenger(event)
        if event_records is None:
            return None
        for event_record in event_records:
            yield event_record.destination_contact

    def get_events_registered(self) -> Iterable[Tuple[Type[Event], Iterable[EventConsumer], Iterable[str]]]:
        for event_records in self.__redis_repository.all():
            event = event_records[0].passenger
            event_consumers = []
            event_consumer_contacts = []
            for event_record in event_records:
                event_consumers.append(event_record.destination)
                event_consumer_contacts.append(event_record.destination_contact)
            yield event, event_consumers, event_consumer_contacts

    def get_event_destinations(self, event: Type[Event]) -> Optional[Iterable[EventConsumer]]:
        event_records: Optional[
            List[PassengerRecord[Event, EventConsumer]]
        ] = self.__redis_repository.filter_by_passenger(event)
        if event_records is None:
            return None
        for event_record in event_records:
            if event_record.destination is None:
                continue
            yield event_record.destination

    def unregister(self, event: Type[Event]) -> None:
        self.__redis_repository.delete_by_passenger(event)
