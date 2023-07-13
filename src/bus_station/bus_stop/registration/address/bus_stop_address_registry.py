from abc import ABCMeta, abstractmethod
from typing import Optional, Type, TypeVar

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.passengers.passenger import Passenger

BT = TypeVar("BT", bound=BusStop)
PT = TypeVar("PT", bound=Passenger)


class BusStopAddressRegistry(metaclass=ABCMeta):
    @abstractmethod
    def register(self, bus_stop_class: Type[BT], address: str) -> None:
        pass

    @abstractmethod
    def get_address_for_bus_stop_passenger_class(self, bus_stop_passenger_class: Type[PT]) -> Optional[str]:
        pass

    @abstractmethod
    def unregister(self, bus_stop_class: Type[BT]) -> None:
        pass
