from typing import Dict, Optional

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.bus_stop.resolvers.bus_stop_resolver import BusStopResolver
from bus_station.shared_terminal.fqn import resolve_fqn


class InMemoryBusStopResolver(BusStopResolver):
    def __init__(self):
        self.__bus_stops: Dict[str, BusStop] = {}

    def add_bus_stop(self, bus_stop: BusStop) -> None:
        fqn = resolve_fqn(bus_stop)
        self.__bus_stops[fqn] = bus_stop

    def resolve(self, bus_stop_id: str) -> Optional[BusStop]:
        return self.__bus_stops.get(bus_stop_id)
