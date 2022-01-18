from abc import abstractmethod
from typing import List, TypeVar, Generic, Optional, Any, Type, Tuple, Iterable

from bus_station.passengers.middleware.passenger_middleware import PassengerMiddleware
from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.bus_stop import BusStop

M = TypeVar("M", bound=PassengerMiddleware)
S = TypeVar("S", bound=BusStop)
P = TypeVar("P", bound=Passenger)


class PassengerMiddlewareExecutor(Generic[P, M, S]):
    def __init__(self):
        self._middleware_definitions: List[M | Tuple[Type[M], Tuple[Any]]] = list()

    def add_middleware_definition(
        self, passenger_middleware_cls: Type[M], *middleware_args: Any, lazy: bool = False
    ) -> None:
        if lazy is False:
            self._middleware_definitions.append(passenger_middleware_cls(*middleware_args))
        else:
            self._middleware_definitions.append((passenger_middleware_cls, middleware_args))

    def _get_middlewares(self) -> Iterable[M]:
        for middleware_definition in self._middleware_definitions:
            if isinstance(middleware_definition, tuple):
                middleware_cls, middleware_args = middleware_definition
                yield middleware_cls(*middleware_args)  # pyre-ignore[19]
            else:
                yield middleware_definition

    @abstractmethod
    def execute(self, passenger: P, passenger_bus_stop: S) -> Optional[Any]:
        pass
