from abc import abstractmethod
from typing import Any, NoReturn, Protocol, TypeVar

from bus_station.passengers.passenger import Passenger

P = TypeVar("P", bound=Passenger)


class Bus(Protocol[P]):
    @abstractmethod
    def transport(self, passenger: P) -> Any | NoReturn:
        pass
