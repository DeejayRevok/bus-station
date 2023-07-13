from typing import Dict, Generic, Optional, Set, TypeVar

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.passengers.passenger_registry import passenger_bus_stop_registry

S = TypeVar("S", bound=BusStop)


class BusStopRegistry(Generic[S]):
    def __init__(self):
        self.__registered_bus_stops: Set[S] = set()
        self.__bus_stop_name_mapping: Dict[str, S] = {}

    def register(self, bus_stop: S) -> None:
        self.__add_bus_stop_to_name_mapping(bus_stop)
        self.__registered_bus_stops.add(bus_stop)
        self.__register_in_passenger_registry(bus_stop)

    def __add_bus_stop_to_name_mapping(self, bus_stop: S) -> None:
        self.__bus_stop_name_mapping[bus_stop.bus_stop_name()] = bus_stop

    def __register_in_passenger_registry(self, bus_stop: S) -> None:
        passenger_bus_stop_registry.register(bus_stop.passenger().passenger_name(), bus_stop.bus_stop_name())

    def unregister(self, bus_stop: S) -> None:
        self.__remove_bus_stop_from_name_mapping(bus_stop)
        self.__registered_bus_stops.remove(bus_stop)
        self.__unregister_in_passenger_registry(bus_stop)

    def __remove_bus_stop_from_name_mapping(self, bus_stop: S) -> None:
        del self.__bus_stop_name_mapping[bus_stop.bus_stop_name()]

    def __unregister_in_passenger_registry(self, bus_stop: S) -> None:
        passenger_bus_stop_registry.unregister(bus_stop.passenger().passenger_name(), bus_stop.bus_stop_name())

    def get_bus_stop_by_name(self, bus_stop_name: str) -> Optional[S]:
        return self.__bus_stop_name_mapping.get(bus_stop_name)
