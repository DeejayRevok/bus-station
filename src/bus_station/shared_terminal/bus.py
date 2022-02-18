from typing import Any, Generic, Type, TypeVar

from bus_station.passengers.middleware.passenger_middleware import PassengerMiddleware
from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor

M = TypeVar("M", bound=PassengerMiddleware)
E = TypeVar("E", bound=PassengerMiddlewareExecutor)


class Bus(Generic[M]):
    def __init__(self, middleware_executor_cls: Type[E]):
        self._middleware_executor = middleware_executor_cls()

    def add_middleware_definition(
        self, passenger_middleware_cls: Type[M], *middleware_args: Any, lazy: bool = False
    ) -> None:
        self._middleware_executor.add_middleware_definition(passenger_middleware_cls, *middleware_args, lazy=lazy)
