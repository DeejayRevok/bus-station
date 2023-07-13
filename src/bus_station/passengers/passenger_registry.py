from collections import defaultdict
from typing import Dict, Set


class __PassengerBusStopRegistry:
    def __init__(self):
        self.__registry: Dict[str, Set[str]] = defaultdict(set)

    def register(self, passenger_name: str, bus_stop_name: str) -> None:
        self.__registry[passenger_name].add(bus_stop_name)

    def get_bus_stops_for_passenger(self, passenger_name: str) -> Set[str]:
        return self.__registry[passenger_name]

    def unregister(self, passenger_name: str, bus_stop_name: str) -> None:
        self.__registry[passenger_name].remove(bus_stop_name)


passenger_bus_stop_registry = __PassengerBusStopRegistry()
