from abc import abstractmethod
from typing import Optional, Protocol, TypeVar

from bus_station.bus_stop.bus_stop import BusStop

S = TypeVar("S", bound=BusStop)


class BusStopResolver(Protocol[S]):
    @abstractmethod
    def resolve(self, bus_stop_id: str) -> Optional[S]:
        pass
