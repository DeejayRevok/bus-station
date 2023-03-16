from contextvars import ContextVar
from typing import Optional
from uuid import uuid4

from bus_station.passengers.passenger import Passenger

__context_distributed_id_var: ContextVar[Optional[str]] = ContextVar(  # pyre-ignore[9]
    "bus_station_distributed_id", default=None
)


def create_distributed_id() -> str:
    distributed_id = str(uuid4())
    __context_distributed_id_var.set(distributed_id)
    return distributed_id


def get_context_distributed_id() -> Optional[str]:
    return __context_distributed_id_var.get()


def get_distributed_id(passenger: Passenger) -> str:
    if passenger.distributed_id is not None:
        __context_distributed_id_var.set(passenger.distributed_id)
        return passenger.distributed_id

    distributed_id = get_context_distributed_id()
    if distributed_id is None:
        distributed_id = create_distributed_id()
    return distributed_id


def clear_context_distributed_id() -> None:
    __context_distributed_id_var.set(None)
