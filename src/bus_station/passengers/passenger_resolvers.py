from importlib import import_module
from typing import Optional, Type, TypeVar, get_type_hints

from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.bus_stop import BusStop

P = TypeVar("P", bound=Passenger)


def resolve_passenger_class_from_fqn(passenger_class_fqn: str) -> Optional[Type[P]]:
    class_components = passenger_class_fqn.rsplit(".", 1)
    module_name = class_components[0]
    class_name = class_components[1]

    module = import_module(module_name)
    return getattr(module, class_name)


def resolve_passenger_class_from_bus_stop(
    bus_stop: BusStop, bus_stop_handle_function_name: str, passenger_type_name: str, expected_passenger_type: Type[P]
) -> Type[P]:
    bus_stop_handle_function = getattr(bus_stop, bus_stop_handle_function_name)
    bus_stop_handle_typing = get_type_hints(bus_stop_handle_function)

    if passenger_type_name not in bus_stop_handle_typing:
        raise TypeError(
            f"{bus_stop_handle_function_name} {passenger_type_name} not found for {bus_stop.bus_stop_name()}"
        )

    bus_stop_passenger_type = bus_stop_handle_typing[passenger_type_name]
    if not issubclass(bus_stop_passenger_type, expected_passenger_type):
        raise TypeError(
            f"Wrong type for {bus_stop_handle_function_name} {passenger_type_name} of {bus_stop.bus_stop_name()}"
        )

    return bus_stop_passenger_type