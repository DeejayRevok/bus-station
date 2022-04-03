from abc import abstractmethod
from typing import TypeVar, Protocol, NoReturn, Any

from bus_station.passengers.passenger import Passenger

P = TypeVar("P", bound=Passenger)


class Bus(Protocol[P]):
    @abstractmethod
    def transport(self, passenger: P) -> Any | NoReturn:
        pass
