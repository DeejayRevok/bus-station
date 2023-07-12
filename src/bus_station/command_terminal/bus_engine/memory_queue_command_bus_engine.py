from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_not_found import CommandHandlerNotFound
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.passengers.memory_queue_passenger_worker import MemoryQueuePassengerWorker
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.engine.engine import Engine
from bus_station.shared_terminal.factories.memory_queue_factory import memory_queue_factory


class MemoryQueueCommandBusEngine(Engine):
    def __init__(
        self,
        command_handler_registry: CommandHandlerRegistry,
        command_receiver: PassengerReceiver[Command, CommandHandler],
        command_deserializer: PassengerDeserializer,
        command_handler_name: str,
    ):
        command_handler = command_handler_registry.get_bus_stop_by_name(command_handler_name)
        if command_handler is None:
            raise CommandHandlerNotFound(command_handler_name)

        command = command_handler.passenger()
        command_queue = memory_queue_factory.queue_with_id(command.passenger_name())
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
