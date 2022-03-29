from importlib import import_module
from typing import Optional, Type

from bus_station.passengers.passenger import Passenger


class PassengerClassResolver:
    def resolve_from_fqn(self, passenger_class_fqn: str) -> Optional[Type[Passenger]]:
        class_components = passenger_class_fqn.rsplit(".", 1)
        module_name = class_components[0]
        class_name = class_components[1]

        module = import_module(module_name)
        return getattr(module, class_name)
