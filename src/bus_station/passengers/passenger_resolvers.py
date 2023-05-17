from typing import Type, get_type_hints

from bus_station.bus_stop.bus_stop import BusStop


def resolve_passenger_class_from_bus_stop(
    bus_stop: BusStop, bus_stop_handle_function_name: str, passenger_type_name: str
) -> Type:
    bus_stop_handle_function = getattr(bus_stop, bus_stop_handle_function_name)
    bus_stop_handle_typing = get_type_hints(bus_stop_handle_function)

    if passenger_type_name not in bus_stop_handle_typing:
        raise TypeError(
            f"{bus_stop_handle_function_name} {passenger_type_name} not found for {bus_stop.bus_stop_name()}"
        )

    return bus_stop_handle_typing[passenger_type_name]
