from abc import abstractmethod
from typing import Any, Optional, Protocol, TypeVar

from bus_station.passengers.passenger import Passenger

P = TypeVar("P", bound=Passenger)


class Bus(Protocol[P]):
    @abstractmethod
    def transport(self, passenger: P) -> Optional[Any]:
        pass
