from abc import ABC
from typing import Type, Iterable, Optional, TypeVar

from redis import Redis

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.registry.destination_registration import DestinationRegistration
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry
from bus_station.passengers.registry.remote_registry import RemoteRegistry
from bus_station.shared_terminal.bus_stop import BusStop


D = TypeVar("D", bound=BusStop)


class RedisRegistry(RemoteRegistry[D], ABC):
    def __init__(self, client: Redis, destination_registry: InMemoryRegistry):
        self.__client = client
        self.__destination_registry = destination_registry

    def register_destination(self, destination: D, destination_contact: str) -> None:
        passenger = self._get_destination_passenger(destination)
        self.__client.set(passenger.__name__, destination_contact.encode("UTF-8"))
        self.__destination_registry.register_destination(destination, destination)

    def get_passenger_destination_registration(self, passenger: Type[Passenger]) -> Optional[DestinationRegistration]:
        destination_contact = self.__client.get(passenger.__name__)
        if destination_contact is None:
            return None
        destination_contact = destination_contact.decode("UTF-8")

        destination = None
        if memory_destination_registration := self.__destination_registry.get_passenger_destination_registration(passenger):
            destination = memory_destination_registration.destination

        return DestinationRegistration(
            destination_contact=destination_contact,
            destination=destination
        )

    def get_registered_passengers(self) -> Iterable[Type[Passenger]]:
        yield from self.__destination_registry.get_registered_passengers()

    def unregister(self, passenger: Type[Passenger]) -> None:
        self.__client.delete(passenger.__name__)
        self.__destination_registry.unregister(passenger)
