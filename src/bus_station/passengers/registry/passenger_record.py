from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Optional, Type, TypeVar

from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.bus_stop import BusStop

P = TypeVar("P", bound=Passenger)
S = TypeVar("S", bound=BusStop)


@dataclass(frozen=True)
class PassengerRecord(Generic[P, S]):
    passenger: Type[P]
    destination: Optional[S]
    destination_contact: Any
