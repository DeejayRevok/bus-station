from abc import abstractmethod
from typing import Any, Generic, Optional, TypeVar

from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.distributed import get_distributed_id

P = TypeVar("P", bound=Passenger)


class Bus(Generic[P]):
    def transport(self, passenger: P) -> Optional[Any]:
        distributed_id = get_distributed_id(passenger)
        passenger.set_distributed_id(distributed_id)

        return self._transport(passenger)

    @abstractmethod
    def _transport(self, passenger: P) -> Optional[Any]:
        pass
