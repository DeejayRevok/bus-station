from abc import abstractmethod
from typing import Any, Generic, Optional, TypeVar

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.context import set_context_root_passenger_id

S = TypeVar("S", bound=BusStop)
P = TypeVar("P", bound=Passenger)


class PassengerReceiver(Generic[P, S]):
    def receive(self, passenger: P, passenger_bus_stop: S) -> Optional[Any]:
        set_context_root_passenger_id(passenger.passenger_id)

        try:
            return self._receive(passenger, passenger_bus_stop)
        finally:
            set_context_root_passenger_id(passenger.root_passenger_id)

    @abstractmethod
    def _receive(self, passenger: P, passenger_bus_stop: S) -> Optional[Any]:
        pass
