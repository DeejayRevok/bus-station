from abc import abstractmethod
from functools import partial
from http.server import ThreadingHTTPServer
from typing import Callable, Dict, Generic, Optional, Type, TypeVar

from jsonrpcserver import Error, Result, Success, method
from jsonrpcserver.codes import ERROR_INTERNAL_ERROR
from jsonrpcserver.server import RequestHandler

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.passengers.passenger import Passenger
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer

P = TypeVar("P", bound=Passenger)
S = TypeVar("S", bound=BusStop)


class JsonRPCServer(Generic[P, S]):
    def __init__(
        self,
        host: str,
        port: int,
        passenger_deserializer: PassengerDeserializer,
        passenger_receiver: PassengerReceiver[P, S],
    ):
        self.__host = host
        self.__port = port
        self._passenger_deserializer = passenger_deserializer
        self._passenger_receiver = passenger_receiver
        self.__internal_registry: Dict[str, Callable] = {}

    def register(self, passenger_class: Type[P], bus_stop: S) -> None:
        exposed_callable = partial(self.__passenger_handler, bus_stop, passenger_class)
        exposed_callable_name = passenger_class.passenger_name()
        self.__internal_registry[exposed_callable_name] = exposed_callable

    def run(self) -> None:
        self.__register_json_rpc_handlers()

        http_server = ThreadingHTTPServer((self.__host, self.__port), RequestHandler)
        try:
            http_server.serve_forever()
        except KeyboardInterrupt:
            http_server.server_close()

    def __register_json_rpc_handlers(self) -> None:
        for exposed_callable_name, exposed_callable in self.__internal_registry.items():
            method(exposed_callable, name=exposed_callable_name)

    def __passenger_handler(
        self, bus_stop: S, passenger_class: Type[P], serialized_passenger: str
    ) -> Result:  # pyre-ignore[11]
        try:
            serialized_response = self._passenger_handler(bus_stop, passenger_class, serialized_passenger)
        except Exception as ex:
            return Error(code=ERROR_INTERNAL_ERROR, message=str(ex))
        return Success(result=serialized_response)

    @abstractmethod
    def _passenger_handler(self, bus_stop: S, passenger_class: Type[P], serialized_passenger: str) -> Optional[str]:
        pass
