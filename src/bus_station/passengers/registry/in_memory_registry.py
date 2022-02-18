from abc import ABC
from typing import Dict, Optional, Type, Iterable, Any, TypeVar

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.registry.destination_registration import DestinationRegistration
from bus_station.passengers.registry.passenger_registry import PassengerRegistry
from bus_station.shared_terminal.bus_stop import BusStop


D = TypeVar("D", bound=BusStop)


class InMemoryRegistry(PassengerRegistry[D, Any], ABC):
    def __init__(self):
        self.__passenger_registry: Dict[Type[Passenger], DestinationRegistration] = dict()

    def register_destination(self, destination: D, destination_contact: Any) -> None:
        passenger = self._get_destination_passenger(destination)
        self.__passenger_registry[passenger] = DestinationRegistration(
            destination_contact=destination_contact,
            destination=destination
        )

    def get_passenger_destination_registration(self, passenger: Type[Passenger]) -> Optional[DestinationRegistration]:
        return self.__passenger_registry.get(passenger)

    def get_registered_passengers(self) -> Iterable[Type[Passenger]]:
        yield from self.__passenger_registry.keys()

    def unregister(self, passenger: Type[Passenger]) -> None:
        if passenger in self.__passenger_registry:
            del self.__passenger_registry[passenger]
