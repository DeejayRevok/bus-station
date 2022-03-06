from typing import Iterable, List, Optional, Type

from redis import Redis

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.registry.in_memory_passenger_record_repository import InMemoryPassengerRecordRepository
from bus_station.passengers.registry.passenger_record import PassengerRecord
from bus_station.passengers.registry.passenger_record_repository import PassengerRecordRepository


class RedisPassengerRecordRepository(PassengerRecordRepository):
    def __init__(self, client: Redis, in_memory_repository: InMemoryPassengerRecordRepository):
        self.__client = client
        self.__in_memory_repository = in_memory_repository

    def save(self, passenger_record: PassengerRecord) -> None:
        if not isinstance(passenger_record.destination_contact, str):
            raise TypeError("Redis repository can only store str destination contacts")

        self.__client.lpush(passenger_record.passenger.__name__, passenger_record.destination_contact.encode("UTF-8"))
        self.__in_memory_repository.save(passenger_record)

    def filter_by_passenger(self, passenger: Type[Passenger]) -> Optional[List[PassengerRecord]]:
        in_memory_records = self.__in_memory_repository.filter_by_passenger(passenger)
        if in_memory_records is not None:
            return in_memory_records

        passenger_key = passenger.__name__
        redis_records = []
        for i in range(0, self.__client.llen(passenger_key)):
            redis_value = self.__client.lindex(passenger_key, i)
            redis_records.append(
                PassengerRecord(passenger=passenger, destination_contact=redis_value.decode("UTF-8"), destination=None)
            )
        if len(redis_records) == 0:
            return None
        return redis_records

    def all(self) -> Iterable[List[PassengerRecord]]:
        yield from self.__in_memory_repository.all()

    def delete_by_passenger(self, passenger: Type[Passenger]) -> None:
        passenger_key = passenger.__name__
        self.__client.delete(passenger_key)
        self.__in_memory_repository.delete_by_passenger(passenger)
