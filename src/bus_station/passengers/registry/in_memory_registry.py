from typing import Any, Type, Optional, Dict

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.registry.passenger_registry import PassengerRegistry


class InMemoryRegistry(PassengerRegistry[Any]):
    def __init__(self):
        self.__passenger_registry: Dict[Type[Passenger], Any] = dict()

    def register(self, passenger: Type[Passenger], destination: Any) -> None:
        self.__passenger_registry[passenger] = destination

    def get_passenger_destination(self, passenger: Type[Passenger]) -> Optional[Any]:
        return self.__passenger_registry.get(passenger)

    def unregister(self, passenger: Type[Passenger]) -> None:
        del self.__passenger_registry[passenger]
