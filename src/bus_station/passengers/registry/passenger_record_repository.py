from abc import abstractmethod
from typing import Iterable, List, Optional, Protocol, Type

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.registry.passenger_record import PassengerRecord


class PassengerRecordRepository(Protocol):
    @abstractmethod
    def save(self, passenger_record: PassengerRecord) -> None:
        pass

    @abstractmethod
    def filter_by_passenger(self, passenger: Type[Passenger]) -> Optional[List[PassengerRecord]]:
        pass

    @abstractmethod
    def all(self) -> Iterable[List[PassengerRecord]]:
        pass

    @abstractmethod
    def delete_by_passenger(self, passenger: Type[Passenger]) -> None:
        pass
