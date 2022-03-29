from typing import Any, Dict, Iterable, List, Optional

from bus_station.passengers.passenger_record.passenger_record import PassengerRecord
from bus_station.passengers.passenger_record.passenger_record_repository import PassengerRecordRepository


class InMemoryPassengerRecordRepository(PassengerRecordRepository):
    def __init__(self):
        self.__passenger_records: Dict[str, List[PassengerRecord[Any]]] = {}

    def save(self, passenger_record: PassengerRecord[Any]) -> None:
        if passenger_record.passenger_name in self.__passenger_records:
            self.__passenger_records[passenger_record.passenger_name].append(passenger_record)
            return
        self.__passenger_records[passenger_record.passenger_name] = [passenger_record]

    def find_by_passenger_name(self, passenger_name: str) -> Optional[List[PassengerRecord]]:
        return self.__passenger_records.get(passenger_name)

    def all(self) -> Iterable[PassengerRecord[Any]]:
        for passenger_records in self.__passenger_records.values():
            for passenger_record in passenger_records:
                yield passenger_record

    def delete_by_passenger_name(self, passenger_name: str) -> None:
        if passenger_name in self.__passenger_records:
            del self.__passenger_records[passenger_name]
