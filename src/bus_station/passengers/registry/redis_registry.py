from typing import Optional, Type

from redis import Redis

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.registry.remote_registry import RemoteRegistry


class RedisRegistry(RemoteRegistry):
    def __init__(self, client: Redis):
        self.__client = client

    def register(self, passenger: Type[Passenger], destination: str) -> None:
        self.__client.set(passenger.__name__, destination.encode("UTF-8"))

    def get_passenger_destination(self, passenger: Type[Passenger]) -> Optional[str]:
        passenger_destination = self.__client.get(passenger.__name__)
        if passenger_destination is None:
            return passenger_destination
        return passenger_destination.decode("UTF-8")

    def unregister(self, passenger: Type[Passenger]) -> None:
        self.__client.delete(passenger.__name__)
