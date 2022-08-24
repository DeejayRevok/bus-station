from typing import Type, TypeVar

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.command_registry import CommandRegistry
from bus_station.passengers.memory_queue_passenger_worker import MemoryQueuePassengerWorker
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.engine.engine import Engine

C = TypeVar("C", bound=Command)


class MemoryQueueCommandBusEngine(Engine):
    def __init__(
        self,
        command_registry: CommandRegistry,
        command_receiver: PassengerReceiver[Command, CommandHandler],
        command_deserializer: PassengerDeserializer,
        command_type: Type[C],
    ):
        super().__init__()
        command_handler = command_registry.get_command_destination(command_type)
        if command_handler is None:
            raise HandlerNotFoundForCommand(command_type.__name__)

        command_queue = command_registry.get_command_destination_contact(command_type)
        self.__command_worker = MemoryQueuePassengerWorker(
            command_queue, command_handler, command_receiver, command_deserializer
        )

    def start(self) -> None:
        try:
            self.__command_worker.work()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        self.__command_worker.stop()
