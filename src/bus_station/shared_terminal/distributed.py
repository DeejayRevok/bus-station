from contextvars import ContextVar, copy_context
from typing import Final, Optional
from uuid import uuid4

__DISTRIBUTED_ID_KEY: Final = "bus_station_distributed_id"


def create_distributed_id() -> str:
    distributed_id = str(uuid4())
    ContextVar(__DISTRIBUTED_ID_KEY).set(distributed_id)
    return distributed_id


def get_context_distributed_id() -> Optional[str]:
    context = copy_context()
    for key, value in context.items():
        if key.name == __DISTRIBUTED_ID_KEY:
            return value
    return None


def get_distributed_id() -> str:
    distributed_id = get_context_distributed_id()
    if distributed_id is None:
        distributed_id = create_distributed_id()
    return distributed_id
