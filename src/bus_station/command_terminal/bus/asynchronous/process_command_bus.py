from multiprocessing import Queue, Process
from typing import Tuple, final, List

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_for_command_already_registered import (
    HandlerForCommandAlreadyRegistered,
)
from bus_station.command_terminal.handler_not_found_for_command import (
    HandlerNotFoundForCommand,
)
from bus_station.passengers.process_passenger_worker import ProcessPassengerWorker
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.runnable import Runnable, is_not_running, is_running


@final
class ProcessCommandBus(CommandBus, Runnable):
    def __init__(
        self,
        command_serializer: PassengerSerializer,
        command_deserializer: PassengerDeserializer,
        command_registry: InMemoryRegistry,
    ):
        CommandBus.__init__(self)
        Runnable.__init__(self)
        self.__command_workers: List[ProcessPassengerWorker] = list()
        self.__command_worker_processes: List[Process] = list()
        self.__command_queues: List[Queue] = list()
        self.__command_serializer = command_serializer
        self.__command_deserializer = command_deserializer
        self.__command_registry = command_registry

    def _start(self) -> None:
        for process in self.__command_worker_processes:
            process.start()

    @is_not_running
    def register(self, handler: CommandHandler) -> None:
        handler_command = self._get_handler_command(handler)
        if handler_command in self.__command_registry:
            raise HandlerForCommandAlreadyRegistered(handler_command.__name__)

        queue, worker, process = self.__create_handler(handler)

        self.__command_registry.register(handler_command, queue)
        self.__command_queues.append(queue)
        self.__command_workers.append(worker)
        self.__command_worker_processes.append(process)

    def __create_handler(self, command_handler: CommandHandler) -> Tuple[Queue, ProcessPassengerWorker, Process]:
        handler_queue = Queue()
        handler_worker = ProcessPassengerWorker(
            handler_queue, command_handler, self._middleware_executor, self.__command_deserializer
        )
        handler_process = Process(target=handler_worker.work)
        return handler_queue, handler_worker, handler_process

    @is_running
    def execute(self, command: Command) -> None:
        command_queue = self.__command_registry.get_passenger_destination(command.__class__)
        if command_queue is None:
            raise HandlerNotFoundForCommand(command.__class__.__name__)
        self.__put_command(command_queue, command)

    def __put_command(self, queue: Queue, command: Command) -> None:
        serialized_command = self.__command_serializer.serialize(command)
        queue.put(serialized_command)

    def _stop(self) -> None:
        for worker in self.__command_workers:
            worker.stop()
        for process in self.__command_worker_processes:
            process.join()
        for queue in self.__command_queues:
            queue.close()
