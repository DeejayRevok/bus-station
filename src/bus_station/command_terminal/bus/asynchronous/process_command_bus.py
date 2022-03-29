from multiprocessing import Process, Queue
from typing import List, Tuple

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.process_passenger_worker import ProcessPassengerWorker
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.bus_stop import BusStop
from bus_station.shared_terminal.runnable import Runnable, is_running


class ProcessCommandBus(CommandBus, Runnable):
    def __init__(
        self,
        command_serializer: PassengerSerializer,
        command_deserializer: PassengerDeserializer,
        command_registry: InMemoryCommandRegistry,
    ):
        CommandBus.__init__(self)
        Runnable.__init__(self)
        self.__command_workers: List[ProcessPassengerWorker] = []
        self.__command_worker_processes: List[Process] = []
        self.__command_serializer = command_serializer
        self.__command_deserializer = command_deserializer
        self.__command_registry = command_registry

    def _start(self) -> None:
        for command in self.__command_registry.get_commands_registered():
            handler = self.__command_registry.get_command_destination(command)
            handler_queue = self.__command_registry.get_command_destination_contact(command)
            worker, process = self.__create_handler(handler, handler_queue)
            self.__command_workers.append(worker)
            self.__command_worker_processes.append(process)
            process.start()

    def __create_handler(
        self, command_handler: BusStop, command_queue: Queue
    ) -> Tuple[ProcessPassengerWorker, Process]:
        handler_worker = ProcessPassengerWorker(
            command_queue, command_handler, self._middleware_executor, self.__command_deserializer
        )
        handler_process = Process(target=handler_worker.work)
        return handler_worker, handler_process

    @is_running
    def execute(self, command: Command) -> None:
        handler_queue = self.__command_registry.get_command_destination_contact(command.__class__)
        if handler_queue is None:
            raise HandlerNotFoundForCommand(command.__class__.__name__)

        self.__put_command(handler_queue, command)

    def __put_command(self, queue: Queue, command: Command) -> None:
        serialized_command = self.__command_serializer.serialize(command)
        queue.put(serialized_command)

    def _stop(self) -> None:
        for worker in self.__command_workers:
            worker.stop()
        for process in self.__command_worker_processes:
            process.join()
