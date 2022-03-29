from abc import abstractmethod
from typing import Iterable, List, Optional, Protocol

from bus_station.passengers.passenger_record.passenger_record import PassengerRecord


class PassengerRecordRepository(Protocol):
    @abstractmethod
    def save(self, passenger_record: PassengerRecord) -> None:
        pass

    @abstractmethod
    def find_by_passenger_name(self, passenger_name: str) -> Optional[List[PassengerRecord]]:
        pass

    @abstractmethod
    def all(self) -> Iterable[PassengerRecord]:
        pass

    @abstractmethod
    def delete_by_passenger_name(self, passenger_name: str) -> None:
        pass
