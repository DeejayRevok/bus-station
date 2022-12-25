from dataclasses import dataclass

from bus_station.passengers.passenger import Passenger


@dataclass(frozen=True)
class Event(Passenger):
    @classmethod
    def passenger_name(cls) -> str:
        return f"event.{cls.__module__}.{cls.__name__}"
