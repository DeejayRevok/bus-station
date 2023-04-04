from typing import Dict, Optional, TypeVar

from bus_station.shared_terminal.bus_stop import BusStop
from bus_station.shared_terminal.bus_stop_resolver.bus_stop_resolver import BusStopResolver
from bus_station.shared_terminal.fqn import resolve_fqn

S = TypeVar("S", bound=BusStop)


class InMemoryBusStopResolver(BusStopResolver[S]):
    def __init__(self):
        self.__bus_stops: Dict[str, S] = {}

    def add_bus_stop(self, bus_stop: S) -> None:
        fqn = resolve_fqn(bus_stop)
        self.__bus_stops[fqn] = bus_stop

    def resolve_from_fqn(self, bus_stop_fqn: str) -> Optional[S]:
        return self.__bus_stops.get(bus_stop_fqn)
