from abc import abstractmethod
from functools import partial
from typing import ClassVar, Generic, Optional, Type, TypeVar

from rpyc import Service

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.bus_stop import BusStop

P = TypeVar("P", bound=Passenger)
S = TypeVar("S", bound=BusStop)


class RPyCService(Service, Generic[P, S]):
    __EXPOSED_CALLABLE_PATTERN: ClassVar[str] = "exposed_{callable_name}"

    def __init__(
        self,
        passenger_deserializer: PassengerDeserializer,
        passenger_receiver: PassengerReceiver,
    ):
        self._passenger_deserializer = passenger_deserializer
        self._passenger_receiver = passenger_receiver

    def register(self, passenger_class: Type[P], bus_stop: S) -> None:
        query_callable = partial(self.passenger_receiver, bus_stop, passenger_class)
        exposed_callable_name = self.__EXPOSED_CALLABLE_PATTERN.format(callable_name=passenger_class.__name__)
        setattr(self, exposed_callable_name, query_callable)

    @abstractmethod
    def passenger_receiver(self, bus_stop: S, passenger_class: Type[P], serialized_passenger: str) -> Optional[str]:
        pass
