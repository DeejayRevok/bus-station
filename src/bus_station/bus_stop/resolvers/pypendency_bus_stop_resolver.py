from typing import Optional, TypeVar

from pypendency.container import Container

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.bus_stop.resolvers.bus_stop_resolver import BusStopResolver

S = TypeVar("S", bound=BusStop)


class PypendencyBusStopResolver(BusStopResolver[S]):
    def __init__(self, pypendency_container: Container):
        self.__pypendency_container = pypendency_container

    def resolve(self, bus_stop_id: str) -> Optional[S]:
        resolved_instance = self.__pypendency_container.get(bus_stop_id)
        if resolved_instance is None:
            return None
        if not issubclass(resolved_instance.__class__, BusStop):
            raise TypeError(f"Instance resolved from {bus_stop_id} is not a valid BusStop")
        return resolved_instance  # type: ignore
