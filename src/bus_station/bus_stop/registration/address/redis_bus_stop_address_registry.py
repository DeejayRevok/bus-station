from typing import Optional, Type, TypeVar

from redis.client import Redis

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.passengers.passenger import Passenger

BT = TypeVar("BT", bound=BusStop)
PT = TypeVar("PT", bound=Passenger)


class RedisBusStopAddressRegistry(BusStopAddressRegistry):
    def __init__(self, redis_client: Redis):
        self.__redis_client = redis_client

    def register(self, bus_stop_class: Type[BT], address: str) -> None:
        bus_stop_name = bus_stop_class.bus_stop_name()
        passenger_name = bus_stop_class.passenger().passenger_name()
        self.__redis_client.set(passenger_name, bus_stop_name)
        self.__redis_client.set(bus_stop_name, address)

    def get_address_for_bus_stop_passenger_class(self, bus_stop_passenger_class: Type[PT]) -> Optional[str]:
        bus_stop_name = self.__redis_client.get(bus_stop_passenger_class.passenger_name())
        return self.__redis_client.get(bus_stop_name).decode("UTF-8")

    def unregister(self, bus_stop_class: Type[BT]) -> None:
        self.__redis_client.delete(bus_stop_class.passenger().passenger_name())
        self.__redis_client.delete(bus_stop_class.bus_stop_name())
