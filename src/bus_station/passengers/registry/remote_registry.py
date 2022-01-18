from typing import Protocol

from bus_station.passengers.registry.passenger_registry import PassengerRegistry


class RemoteRegistry(PassengerRegistry[str], Protocol):
    pass
