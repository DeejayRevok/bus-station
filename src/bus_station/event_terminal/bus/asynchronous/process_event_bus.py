from multiprocessing import Process, Queue
from typing import List, Tuple

from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry
from bus_station.passengers.process_passenger_worker import ProcessPassengerWorker
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.runnable import Runnable, is_running


class ProcessEventBus(EventBus, Runnable):
    def __init__(
        self,
        event_serializer: PassengerSerializer,
        event_deserializer: PassengerDeserializer,
        event_registry: InMemoryEventRegistry,
        event_receiver: PassengerReceiver[Event, EventConsumer],
    ):
        EventBus.__init__(self, event_receiver)
        Runnable.__init__(self)
        self.__event_workers: List[ProcessPassengerWorker] = []
        self.__event_worker_processes: List[Process] = []
        self.__event_serializer = event_serializer
        self.__event_deserializer = event_deserializer
        self.__event_registry = event_registry

    def _start(self) -> None:
        for event in self.__event_registry.get_events_registered():
            consumers = self.__event_registry.get_event_destinations(event)
            consumer_queues = self.__event_registry.get_event_destination_contacts(event)
            if consumers is None or consumer_queues is None:
                continue
            for consumer, consumer_queue in zip(consumers, consumer_queues):
                worker, process = self.__create_consumer(consumer, consumer_queue)
                process.start()
                self.__event_workers.append(worker)
                self.__event_worker_processes.append(process)

    def __create_consumer(
        self, consumer: EventConsumer, consumer_queue: Queue
    ) -> Tuple[ProcessPassengerWorker, Process]:
        consumer_worker = ProcessPassengerWorker(
            consumer_queue, consumer, self._event_receiver, self.__event_deserializer
        )
        consumer_process = Process(target=consumer_worker.work)
        return consumer_worker, consumer_process

    @is_running
    def transport(self, passenger: Event) -> None:
        event_consumer_queues = self.__event_registry.get_event_destination_contacts(passenger.__class__)
        if event_consumer_queues is None:
            return

        for event_queue in event_consumer_queues:
            self.__put_event(event_queue, passenger)

    def __put_event(self, queue: Queue, event: Event) -> None:
        serialized_event = self.__event_serializer.serialize(event)
        queue.put(serialized_event)

    def _stop(self) -> None:
        for worker in self.__event_workers:
            worker.stop()
        for process in self.__event_worker_processes:
            process.join()
