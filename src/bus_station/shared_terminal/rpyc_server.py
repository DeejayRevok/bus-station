from abc import abstractmethod
from functools import partial
from typing import Callable, ClassVar, Dict, Generic, Optional, Type, TypeVar

from rpyc import Service, ThreadedServer

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.bus_stop import BusStop

P = TypeVar("P", bound=Passenger)
S = TypeVar("S", bound=BusStop)


class RPyCServer(Generic[P, S]):
    __SELF_HOST_ADDR: ClassVar[str] = "127.0.0.1"
    __EXPOSED_CALLABLE_PATTERN: ClassVar[str] = "exposed_{callable_name}"

    def __init__(
        self,
        port: int,
        passenger_deserializer: PassengerDeserializer,
        passenger_receiver: PassengerReceiver,
    ):
        self._passenger_deserializer = passenger_deserializer
        self._passenger_receiver = passenger_receiver
        self.__port = port
        self.__callables_to_expose: Dict[str, Callable] = {}

    def register(self, passenger_class: Type[P], bus_stop: S) -> None:
        exposed_callable = partial(self._passenger_handler, bus_stop, passenger_class)
        exposed_callable_name = self.__EXPOSED_CALLABLE_PATTERN.format(callable_name=passenger_class.__name__)
        self.__callables_to_expose[exposed_callable_name] = exposed_callable

    def run(self) -> None:
        rpyc_server = ThreadedServer(
            service=self.__build_rpyc_service(),
            hostname=self.__SELF_HOST_ADDR,
            port=self.__port,
            protocol_config={"allow_public_attrs": True},
        )
        rpyc_server.start()
        rpyc_server.close()

    def __build_rpyc_service(self) -> Service:
        rpyc_service_class = type("RPyCServiceClass", (Service,), self.__callables_to_expose)
        return rpyc_service_class()

    @abstractmethod
    def _passenger_handler(self, bus_stop: S, passenger_class: Type[P], serialized_passenger: str) -> Optional[str]:
        pass
