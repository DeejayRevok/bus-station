from typing import Optional, TypeVar

from pypendency.container import Container

from bus_station.shared_terminal.bus_stop import BusStop
from bus_station.shared_terminal.bus_stop_resolver.bus_stop_resolver import BusStopResolver

S = TypeVar("S", bound=BusStop)


class PypendencyBusStopResolver(BusStopResolver[S]):
    def __init__(self, pypendency_container: Container):
        self.__pypendency_container = pypendency_container

    def resolve_from_fqn(self, bus_stop_fqn: str) -> Optional[S]:
        resolved_instance = self.__pypendency_container.get(bus_stop_fqn)
        if resolved_instance is None:
            return None
        if not issubclass(resolved_instance.__class__, BusStop):
            raise TypeError(f"Instance resolved from {bus_stop_fqn} is not a valid BusStop")
        return resolved_instance  # type: ignore
