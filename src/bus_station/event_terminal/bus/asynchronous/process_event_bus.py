from multiprocessing import Queue, Process
from typing import Tuple, List, final

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.passengers.process_passenger_worker import ProcessPassengerWorker
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.runnable import Runnable, is_not_running, is_running


@final
class ProcessEventBus(EventBus, Runnable):
    def __init__(
        self,
        event_serializer: PassengerSerializer,
        event_deserializer: PassengerDeserializer,
        event_registry: InMemoryRegistry,
    ):
        EventBus.__init__(self)
        Runnable.__init__(self)
        self.__event_queues: List[Queue] = list()
        self.__event_workers: List[ProcessPassengerWorker] = list()
        self.__event_worker_processes: List[Process] = list()
        self.__event_serializer = event_serializer
        self.__event_deserializer = event_deserializer
        self.__event_registry = event_registry

    def _start(self) -> None:
        for process in self.__event_worker_processes:
            process.start()

    @is_not_running
    def register(self, handler: EventConsumer) -> None:
        consumer_event = self._get_consumer_event(handler)
        event_consumer_queues = self.__event_registry.get_passenger_destination(consumer_event)
        if event_consumer_queues is not None:
            queue, worker, worker_process = self.__create_consumer(handler)
            event_consumer_queues.append(queue)
            self.__event_queues.append(queue)
            self.__event_workers.append(worker)
            self.__event_worker_processes.append(worker_process)
        else:
            queue, worker, worker_process = self.__create_consumer(handler)
            self.__event_registry.register(consumer_event, [queue])
            self.__event_queues.append(queue)
            self.__event_workers.append(worker)
            self.__event_worker_processes.append(worker_process)

    def __create_consumer(self, consumer: EventConsumer) -> Tuple[Queue, ProcessPassengerWorker, Process]:
        consumer_queue = Queue()
        consumer_worker = ProcessPassengerWorker(
            consumer_queue, consumer, self._middleware_executor, self.__event_deserializer
        )
        consumer_process = Process(target=consumer_worker.work)
        return consumer_queue, consumer_worker, consumer_process

    @is_running
    def publish(self, event: Event) -> None:
        event_consumer_queues = self.__event_registry.get_passenger_destination(event.__class__)
        if event_consumer_queues is not None:
            for event_queue in event_consumer_queues:
                self.__put_event(event_queue, event)

    def __put_event(self, queue: Queue, event: Event) -> None:
        serialized_event = self.__event_serializer.serialize(event)
        queue.put(serialized_event)

    def _stop(self) -> None:
        for worker in self.__event_workers:
            worker.stop()
        for process in self.__event_worker_processes:
            process.join()
        for queue in self.__event_queues:
            queue.close()
