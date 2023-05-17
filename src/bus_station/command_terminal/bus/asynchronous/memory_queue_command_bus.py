from multiprocessing import Queue

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.factories.memory_queue_factory import memory_queue_factory


class MemoryQueueCommandBus(CommandBus):
    def __init__(
        self,
        command_serializer: PassengerSerializer,
    ):
        self.__command_serializer = command_serializer

    def _transport(self, passenger: Command) -> None:
        queue = memory_queue_factory.queue_with_id(passenger.passenger_name())
        self.__put_command(queue, passenger)

    def __put_command(self, queue: Queue, command: Command) -> None:
        serialized_command = self.__command_serializer.serialize(command)
        queue.put(serialized_command)
