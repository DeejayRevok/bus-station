from multiprocessing import Queue

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class MemoryQueueCommandBus(CommandBus):
    def __init__(
        self,
        command_serializer: PassengerSerializer,
        command_registry: InMemoryCommandRegistry,
    ):
        self.__command_serializer = command_serializer
        self.__command_registry = command_registry

    def transport(self, passenger: Command) -> None:
        handler_queue = self.__command_registry.get_command_destination_contact(passenger.__class__)
        if handler_queue is None:
            raise HandlerNotFoundForCommand(passenger.__class__.__name__)

        self.__put_command(handler_queue, passenger)

    def __put_command(self, queue: Queue, command: Command) -> None:
        serialized_command = self.__command_serializer.serialize(command)
        queue.put(serialized_command)
