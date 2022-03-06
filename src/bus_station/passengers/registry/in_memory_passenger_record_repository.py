from typing import Dict, Iterable, List, Optional, Type

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.registry.passenger_record import PassengerRecord
from bus_station.passengers.registry.passenger_record_repository import PassengerRecordRepository


class InMemoryPassengerRecordRepository(PassengerRecordRepository):
    def __init__(self):
        self.__passenger_records: Dict[str, List[PassengerRecord]] = {}

    def save(self, passenger_record: PassengerRecord) -> None:
        if passenger_record.passenger.__name__ in self.__passenger_records:
            self.__passenger_records[passenger_record.passenger.__name__].append(passenger_record)
            return
        self.__passenger_records[passenger_record.passenger.__name__] = [passenger_record]

    def filter_by_passenger(self, passenger: Type[Passenger]) -> Optional[List[PassengerRecord]]:
        passenger_key = passenger.__name__
        return self.__passenger_records.get(passenger_key)

    def all(self) -> Iterable[List[PassengerRecord]]:
        return self.__passenger_records.values()

    def delete_by_passenger(self, passenger: Type[Passenger]) -> None:
        passenger_key = passenger.__name__
        if passenger_key in self.__passenger_records:
            del self.__passenger_records[passenger_key]
