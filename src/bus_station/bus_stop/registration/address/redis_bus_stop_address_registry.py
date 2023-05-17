from typing import Optional

from redis.client import Redis

from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry


class RedisBusStopAddressRegistry(BusStopAddressRegistry):
    def __init__(self, redis_client: Redis):
        self.__redis_client = redis_client

    def register(self, bus_stop_id: str, address: str) -> None:
        self.__redis_client.set(bus_stop_id, address)

    def get_bus_stop_address(self, bus_stop_id: str) -> Optional[str]:
        return self.__redis_client.get(bus_stop_id).decode("UTF-8")

    def unregister(self, bus_stop_id: str) -> None:
        self.__redis_client.delete(bus_stop_id)
