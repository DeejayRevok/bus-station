from abc import abstractmethod
from typing import Any, Optional, Protocol, TypeVar

from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.bus_stop import BusStop

S = TypeVar("S", bound=BusStop)
P = TypeVar("P", bound=Passenger)


class PassengerReceiver(Protocol[P, S]):
    @abstractmethod
    def receive(self, passenger: P, passenger_bus_stop: S) -> Optional[Any]:
        pass
