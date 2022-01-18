from dataclasses import dataclass

from bus_station.passengers.passenger import Passenger


@dataclass(frozen=True)
class Command(Passenger):
    pass
