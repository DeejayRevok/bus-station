from typing import Protocol, TypeVar

from bus_station.passengers.registry.passenger_registry import PassengerRegistry
from bus_station.shared_terminal.bus_stop import BusStop


D = TypeVar("D", bound=BusStop)


class RemoteRegistry(PassengerRegistry[D, str], Protocol[D]):
    pass
