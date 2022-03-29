from abc import abstractmethod
from typing import Protocol

from bus_station.passengers.passenger import Passenger


class PassengerSerializer(Protocol):
    @abstractmethod
    def serialize(self, passenger: Passenger) -> str:
        pass
