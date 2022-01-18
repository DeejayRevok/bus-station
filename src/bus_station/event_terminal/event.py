from dataclasses import dataclass

from bus_station.passengers.passenger import Passenger


@dataclass(frozen=True)
class Event(Passenger):
    pass
