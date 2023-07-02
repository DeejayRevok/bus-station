from importlib import import_module
from typing import Optional, Type, TypeVar

from yandil.container import Container, default_container

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.bus_stop.resolvers.bus_stop_resolver import BusStopResolver

S = TypeVar("S", bound=BusStop)


class YandilBusStopResolver(BusStopResolver[S]):
    def __init__(self, container: Optional[Container] = None):
        self.__container = container or default_container

    def resolve(self, bus_stop_fqn: str) -> Optional[S]:
        bus_stop_class = self.__get_class_from_fqn(bus_stop_fqn)
        if bus_stop_class is None:
            return None

        bus_stop_instance = self.__container[bus_stop_class]
        if not isinstance(bus_stop_instance, BusStop):
            raise TypeError(f"Instance resolved from {bus_stop_fqn} is not a valid BusStop")
        return bus_stop_instance

    def __get_class_from_fqn(self, fqn: str) -> Type:
        module_name, class_qualname = fqn.rsplit(".", 1)
        module = import_module(module_name)
        return getattr(module, class_qualname)
