from abc import abstractmethod
from typing import Protocol, Type, Optional

from bus_station.passengers.passenger import Passenger


class PassengerDeserializer(Protocol):
    @abstractmethod
    def deserialize(self, passenger_serialized: str, passenger_cls: Optional[Type[Passenger]] = None) -> Passenger:
        pass
