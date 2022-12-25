from dataclasses import dataclass

from bus_station.passengers.passenger import Passenger


@dataclass(frozen=True)
class Query(Passenger):
    @classmethod
    def passenger_name(cls) -> str:
        return f"query.{cls.__module__}.{cls.__name__}"
