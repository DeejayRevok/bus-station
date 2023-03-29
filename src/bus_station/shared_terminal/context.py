from contextvars import ContextVar
from typing import Optional

__context_root_passenger_id: ContextVar[Optional[str]] = ContextVar(  # pyre-ignore[9]
    "bus_station_root_passenger_id", default=None
)


def set_context_root_passenger_id(root_passenger_id: Optional[str]) -> None:
    __context_root_passenger_id.set(root_passenger_id)


def get_context_root_passenger_id() -> Optional[str]:
    return __context_root_passenger_id.get()
