from importlib import import_module
from typing import Optional, Type

from yandil.container import Container, default_container  # pyre-ignore[21]

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.bus_stop.resolvers.bus_stop_resolver import BusStopResolver


class YandilBusStopResolver(BusStopResolver):
    def __init__(self, container: Optional[Container] = None):  # pyre-ignore[11]
        self.__container = container or default_container

    def resolve(self, bus_stop_id: str) -> Optional[BusStop]:
        bus_stop_class = self.__get_class_from_fqn(bus_stop_id)
        if bus_stop_class is None:
            return None

        resolved_bus_stop = self.__container[bus_stop_class]

        if not issubclass(resolved_bus_stop.__class__, BusStop):
            raise TypeError(f"Instance resolved from {bus_stop_id} is not a valid BusStop")

        return resolved_bus_stop

    def __get_class_from_fqn(self, fqn: str) -> Type:
        module_name, class_qualname = fqn.rsplit(".", 1)
        module = import_module(module_name)
        return getattr(module, class_qualname)
