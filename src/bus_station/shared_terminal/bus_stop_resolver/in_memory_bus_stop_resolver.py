from typing import Dict, Optional, TypeVar

from bus_station.shared_terminal.bus_stop import BusStop
from bus_station.shared_terminal.bus_stop_resolver.bus_stop_resolver import BusStopResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter

S = TypeVar("S", bound=BusStop)


class InMemoryBusStopResolver(BusStopResolver[S]):
    def __init__(self, fqn_getter: FQNGetter):
        self.__fqn_getter = fqn_getter
        self.__bus_stops: Dict[str, S] = {}

    def add_bus_stop(self, bus_stop: S) -> None:
        fqn = self.__fqn_getter.get(bus_stop)
        self.__bus_stops[fqn] = bus_stop

    def resolve_from_fqn(self, bus_stop_fqn: str) -> Optional[S]:
        return self.__bus_stops.get(bus_stop_fqn)
