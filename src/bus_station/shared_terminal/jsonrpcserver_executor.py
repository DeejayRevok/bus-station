from abc import abstractmethod
from functools import partial
from typing import TypeVar, Generic, Type, Dict, Callable

from jsonrpcserver import method, serve, Success
from jsonrpcserver.result import SuccessResult, ErrorResult
from oslash import Either

from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor
from bus_station.passengers.passenger import Passenger
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.bus_stop import BusStop

P = TypeVar("P", bound=Passenger)
S = TypeVar("S", bound=BusStop)


class JsonrpcserverExecutor(Generic[P, S]):

    def __init__(
        self,
        passenger_deserializer: PassengerDeserializer,
        passenger_middleware_executor: PassengerMiddlewareExecutor,
    ):
        self._passenger_deserializer = passenger_deserializer
        self._passenger_middleware_executor = passenger_middleware_executor
        self.__internal_registry: Dict[str, Callable] = {}

    def register(self, passenger_class: Type[P], bus_stop: S) -> None:
        exposed_callable = partial(self.passenger_executor, bus_stop, passenger_class)
        exposed_callable_name = passenger_class.__name__
        self.__internal_registry[exposed_callable_name] = exposed_callable

    def run(self, port: int) -> None:
        for exposed_callable_name, exposed_callable in self.__internal_registry.items():
            method(exposed_callable, name=exposed_callable_name)
        try:
            serve(port=port)
        except KeyboardInterrupt:
            pass

    def passenger_executor(self, bus_stop: S, passenger_class: Type[P], serialized_passenger: str) -> Either[ErrorResult, SuccessResult]:
        self._passenger_executor(bus_stop, passenger_class, serialized_passenger)
        return Success()

    @abstractmethod
    def _passenger_executor(self, bus_stop: S, passenger_class: Type[P], serialized_passenger: str) -> None:
        pass
