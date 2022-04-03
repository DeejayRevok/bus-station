from ctypes import c_bool
from multiprocessing import Queue, Value
from queue import Empty

from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.bus_stop import BusStop


class ProcessPassengerWorker:
    def __init__(
        self,
        queue: Queue,
        passenger_bus_stop: BusStop,
        passenger_receiver: PassengerReceiver,
        passenger_deserializer: PassengerDeserializer,
    ):
        self.__queue = queue
        self.__passenger_bus_stop = passenger_bus_stop
        self.__passenger_deserializer = passenger_deserializer
        self.__passenger_receiver = passenger_receiver
        self.__running = Value(c_bool, False)

    def work(self) -> None:
        self.__running.value = True
        while self.__running.value:
            try:
                item = self.__queue.get(timeout=1.0)
            except Empty:
                continue
            except KeyboardInterrupt:
                self.__running.value = False
                continue
            self.__handle_item(item)

    def __handle_item(self, item: str) -> None:
        deserialized_item = self.__passenger_deserializer.deserialize(item)
        self.__passenger_receiver.receive(deserialized_item, self.__passenger_bus_stop)

    def stop(self):
        self.__running.value = False
