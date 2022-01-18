from abc import abstractmethod
from typing import Optional, Type, TypeVar, Protocol

from bus_station.passengers.passenger import Passenger


D = TypeVar("D")


class PassengerRegistry(Protocol[D]):
    @abstractmethod
    def register(self, passenger: Type[Passenger], destination: D) -> None:
        pass

    @abstractmethod
    def get_passenger_destination(self, passenger: Type[Passenger]) -> Optional[D]:
        pass

    @abstractmethod
    def unregister(self, passenger: Type[Passenger]) -> None:
        pass

    def __contains__(self, passenger: Type[Passenger]) -> bool:
        passenger_destination = self.get_passenger_destination(passenger)
        if passenger_destination is None:
            return False
        return True
