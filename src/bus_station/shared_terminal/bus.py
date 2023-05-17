# pyre-ignore-all-errors
from abc import abstractmethod
from typing import Any, Generic, Optional, TypeVar

from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.context import get_context_root_passenger_id
from bus_station.shared_terminal.dataclass_type import DataclassType

P = TypeVar("P", bound=Passenger)


class Bus(Generic[P]):
    def transport(self, passenger: P | DataclassType) -> Optional[Any]:
        root_passenger_id = get_context_root_passenger_id()
        passenger.set_root_passenger_id(root_passenger_id)

        return self._transport(passenger)

    @abstractmethod
    def _transport(self, passenger: P) -> Optional[Any]:
        pass
