from abc import abstractmethod
from typing import Any, Generic, Optional, TypeVar

from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.bus_stop import BusStop
from bus_station.shared_terminal.distributed import get_distributed_id

S = TypeVar("S", bound=BusStop)
P = TypeVar("P", bound=Passenger)


class PassengerReceiver(Generic[P, S]):
    def receive(self, passenger: P, passenger_bus_stop: S) -> Optional[Any]:
        distributed_id = get_distributed_id()
        passenger.set_distributed_id(distributed_id)

        return self._receive(passenger, passenger_bus_stop)

    @abstractmethod
    def _receive(self, passenger: P, passenger_bus_stop: S) -> Optional[Any]:
        pass
