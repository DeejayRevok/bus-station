from abc import abstractmethod
from functools import partial
from http.server import ThreadingHTTPServer
from typing import Callable, ClassVar, Dict, Generic, Optional, Type, TypeVar

from jsonrpcserver import Error, Success, method
from jsonrpcserver.codes import ERROR_INTERNAL_ERROR
from jsonrpcserver.result import Result
from jsonrpcserver.server import RequestHandler

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.bus_stop import BusStop

P = TypeVar("P", bound=Passenger)
S = TypeVar("S", bound=BusStop)


class JsonRPCServer(Generic[P, S]):

    __SELF_HOST_ADDR: ClassVar[str] = "127.0.0.1"

    def __init__(
        self,
        passenger_deserializer: PassengerDeserializer,
        passenger_receiver: PassengerReceiver[P, S],
    ):
        self._passenger_deserializer = passenger_deserializer
        self._passenger_receiver = passenger_receiver
        self.__internal_registry: Dict[str, Callable] = {}

    def register(self, passenger_class: Type[P], bus_stop: S) -> None:
        exposed_callable = partial(self.passenger_handler, bus_stop, passenger_class)
        exposed_callable_name = passenger_class.__name__
        self.__internal_registry[exposed_callable_name] = exposed_callable

    def run(self, port: int) -> None:
        self.__register_json_rpc_handlers()

        http_server = ThreadingHTTPServer((self.__SELF_HOST_ADDR, port), RequestHandler)
        try:
            http_server.serve_forever()
        except KeyboardInterrupt:
            http_server.server_close()

    def __register_json_rpc_handlers(self) -> None:
        for exposed_callable_name, exposed_callable in self.__internal_registry.items():
            method(exposed_callable, name=exposed_callable_name)

    def passenger_handler(self, bus_stop: S, passenger_class: Type[P], serialized_passenger: str) -> Result:
        try:
            serialized_response = self._passenger_handler(bus_stop, passenger_class, serialized_passenger)
        except Exception as ex:
            return Error(code=ERROR_INTERNAL_ERROR, message=str(ex))
        return Success(result=serialized_response)

    @abstractmethod
    def _passenger_handler(self, bus_stop: S, passenger_class: Type[P], serialized_passenger: str) -> Optional[str]:
        pass
