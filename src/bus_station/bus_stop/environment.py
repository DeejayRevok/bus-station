from os import environ
from re import sub
from typing import Optional

__SEPARATOR = "_"
__BUS_STOP_ADDRESS_ENV_VARIABLE_NAME_PATTERN = f"BUS_STATION{__SEPARATOR}{{formatted_bus_stop_id}}{__SEPARATOR}ADDRESS"
__SYMBOLS_REGEX = r"[^a-zA-Z0-9 \n\.]"


def get_bus_stop_address_from_environment(bus_stop_id: str) -> Optional[str]:
    bus_stop_env_var = get_bus_stop_address_env_variable(bus_stop_id)
    return environ.get(bus_stop_env_var)


def get_bus_stop_address_env_variable(bus_stop_id: str) -> str:
    name_with_separator = sub(__SYMBOLS_REGEX, __SEPARATOR, bus_stop_id)
    return __BUS_STOP_ADDRESS_ENV_VARIABLE_NAME_PATTERN.format(formatted_bus_stop_id=name_with_separator.upper())
