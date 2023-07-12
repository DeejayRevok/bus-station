# pyre-ignore-all-errors[7]
from typing import Callable, Dict, Generic, Optional, Set, TypeVar

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.bus_stop.bus_stop_not_found import BusStopNotFound
from bus_station.bus_stop.resolvers.bus_stop_resolver import BusStopResolver
from bus_station.passengers.passenger_registry import passenger_bus_stop_registry

S = TypeVar("S", bound=BusStop)


class BusStopRegistry(Generic[S]):
    def __init__(
        self,
        bus_stop_resolver: BusStopResolver,
        bus_stop_passenger_resolver: Callable,
    ):
        self._bus_stop_resolver = bus_stop_resolver
        self.__bus_stop_passenger_resolver = bus_stop_passenger_resolver
        self.__registered_bus_stops: Set[str] = set()
        self.__bus_stop_name_id_mapping: Dict[str, str] = {}

    def register(self, bus_stop_id: str) -> None:
        bus_stop = self._bus_stop_resolver.resolve(bus_stop_id)
        if bus_stop is None:
            raise BusStopNotFound(bus_stop_id)
        self.__add_bus_stop_name_mapping(bus_stop_id, bus_stop)
        self.__registered_bus_stops.add(bus_stop_id)
        self.__register_in_passenger_registry(bus_stop_id, bus_stop)

    def __add_bus_stop_name_mapping(self, bus_stop_id: str, bus_stop: BusStop) -> None:
        self.__bus_stop_name_id_mapping[bus_stop.bus_stop_name()] = bus_stop_id

    def __register_in_passenger_registry(self, bus_stop_id: str, bus_stop: BusStop) -> None:
        passenger = self.__bus_stop_passenger_resolver(bus_stop)
        passenger_bus_stop_registry.register(passenger.passenger_name(), bus_stop_id)

    def unregister(self, bus_stop_id: str) -> None:
        bus_stop = self._bus_stop_resolver.resolve(bus_stop_id)
        if bus_stop is None:
            raise BusStopNotFound(bus_stop_id)
        self.__remove_bus_stop_name_mapping(bus_stop)
        self.__registered_bus_stops.remove(bus_stop_id)
        self.__unregister_in_passenger_registry(bus_stop_id)

    def __remove_bus_stop_name_mapping(self, bus_stop: BusStop) -> None:
        del self.__bus_stop_name_id_mapping[bus_stop.bus_stop_name()]

    def __unregister_in_passenger_registry(self, bus_stop_id: str) -> None:
        bus_stop = self._bus_stop_resolver.resolve(bus_stop_id)
        passenger = self.__bus_stop_passenger_resolver(bus_stop)
        passenger_bus_stop_registry.unregister(passenger.passenger_name(), bus_stop_id)

    def get_bus_stop(self, bus_stop_id: str) -> Optional[S]:
        if bus_stop_id not in self.__registered_bus_stops:
            return None
        return self._bus_stop_resolver.resolve(bus_stop_id)

    def get_bus_stop_by_name(self, bus_stop_name: str) -> Optional[S]:
        if bus_stop_name not in self.__bus_stop_name_id_mapping:
            return None
        return self._bus_stop_resolver.resolve(self.__bus_stop_name_id_mapping[bus_stop_name])
