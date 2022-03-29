from abc import abstractmethod
from typing import Optional, Protocol, TypeVar

from bus_station.shared_terminal.bus_stop import BusStop

S = TypeVar("S", bound=BusStop)


class BusStopResolver(Protocol[S]):
    @abstractmethod
    def resolve_from_fqn(self, bus_stop_fqn: str) -> Optional[S]:
        pass
