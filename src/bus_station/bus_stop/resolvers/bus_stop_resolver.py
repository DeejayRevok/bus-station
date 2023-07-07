from abc import abstractmethod
from typing import Optional, Protocol

from bus_station.bus_stop.bus_stop import BusStop


class BusStopResolver(Protocol):
    @abstractmethod
    def resolve(self, bus_stop_id: str) -> Optional[BusStop]:
        pass
