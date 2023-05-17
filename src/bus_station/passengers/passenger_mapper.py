from dataclasses import is_dataclass
from typing import Callable, Optional, Type, TypeVar

from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.dataclass_type import DataclassType

P = TypeVar("P", bound=Passenger)


__EXCLUDED_MAPPING_MEMBERS = {
    "__module__",
    "__init__",
    "__dict__",
    "__weakref__",
    "__doc__",
    "__abstractmethods__",
    "_abc_impl",
}


def passenger_mapper(
    class_to_map: DataclassType, passenger_type: Type[P], passenger_name: Optional[str] = None
) -> None:
    if is_dataclass(class_to_map) is False:
        raise ValueError("Class to map must be a dataclass")

    __copy_class_members(Passenger, class_to_map)
    __copy_class_members(passenger_type, class_to_map)
    __set_mapped_init_fn(passenger_type, class_to_map)
    __set_passenger_name(class_to_map, passenger_name)


def __copy_class_members(source_class: Type, destination_class: DataclassType) -> None:
    for member_name, member_value in source_class.__dict__.items():
        if member_name in __EXCLUDED_MAPPING_MEMBERS:
            continue

        if member_name == "__annotations__":
            destination_class.__annotations__.update(member_value)
            continue

        if member_name == "__dataclass_fields__":
            for field_name, field_value in member_value.items():
                setattr(destination_class, field_name, field_value)

            destination_class.__dataclass_fields__.update(member_value)
            continue

        setattr(destination_class, member_name, member_value)


def __set_mapped_init_fn(passenger_type: Type[P], destination_class: DataclassType) -> None:
    def __new_init_fn(passenger_init_fn: Callable, destination_class_init_fn: Callable) -> Callable:
        def real_init_fn(self, *args, **kwargs) -> None:
            passenger_init_fn(self)
            destination_class_init_fn(self, *args, **kwargs)

        return real_init_fn

    destination_class.__init__ = __new_init_fn(passenger_type.__init__, destination_class.__init__)  # pyre-ignore[8]


def __set_passenger_name(destination_class: DataclassType, passenger_name: Optional[str]) -> None:
    if passenger_name is None:
        return

    setattr(destination_class, "passenger_name", lambda *_: passenger_name)
