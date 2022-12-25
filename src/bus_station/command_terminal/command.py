from dataclasses import dataclass

from bus_station.passengers.passenger import Passenger


@dataclass(frozen=True)
class Command(Passenger):
    @classmethod
    def passenger_name(cls) -> str:
        return f"command.{cls.__module__}.{cls.__name__}"
