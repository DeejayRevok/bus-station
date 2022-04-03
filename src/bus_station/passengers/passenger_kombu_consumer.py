from ctypes import c_bool
from multiprocessing import Value
from typing import Callable, List, Type

from kombu import Connection, Message
from kombu.messaging import Consumer as KombuConsumer
from kombu.messaging import Queue
from kombu.mixins import ConsumerMixin
from kombu.transport.virtual import Channel

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.bus_stop import BusStop


class PassengerKombuConsumer(ConsumerMixin):
    def __init__(
        self,
        connection: Connection,
        passenger_queue: Queue,
        passenger_bus_stop: BusStop,
        passenger_class: Type[Passenger],
        passenger_receiver: PassengerReceiver,
        passenger_deserializer: PassengerDeserializer,
    ):
        self.connection = connection
        self.__should_stop = Value(c_bool, False)
        self.__queue = passenger_queue
        self.__passenger_bus_stop = passenger_bus_stop
        self.__passenger_class = passenger_class
        self.__passenger_receiver = passenger_receiver
        self.__passenger_deserializer = passenger_deserializer

    @property
    def should_stop(self):
        return self.__should_stop.value

    @should_stop.setter
    def should_stop(self, value):
        self.__should_stop.value = value

    def get_consumers(self, Consumer: Callable, channel: Channel) -> List[KombuConsumer]:
        return [
            Consumer(queues=[self.__queue], callbacks=[self.on_message]),
        ]

    def on_message(self, body: str, message: Message) -> None:
        passenger = self.__passenger_deserializer.deserialize(body, passenger_cls=self.__passenger_class)
        try:
            self.__passenger_receiver.receive(passenger, self.__passenger_bus_stop)
            message.ack()
        except Exception:
            message.reject(requeue=False)

    def stop(self):
        self.should_stop = True
