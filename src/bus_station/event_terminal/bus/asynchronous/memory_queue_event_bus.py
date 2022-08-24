from multiprocessing import Queue

from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class MemoryQueueEventBus(EventBus):
    def __init__(
        self,
        event_serializer: PassengerSerializer,
        event_registry: InMemoryEventRegistry,
    ):
        self.__event_serializer = event_serializer
        self.__event_registry = event_registry

    def transport(self, passenger: Event) -> None:
        event_consumer_queues = self.__event_registry.get_event_destination_contacts(passenger.__class__)
        if event_consumer_queues is None:
            return

        for event_queue in event_consumer_queues:
            self.__put_event(event_queue, passenger)

    def __put_event(self, queue: Queue, event: Event) -> None:
        serialized_event = self.__event_serializer.serialize(event)
        queue.put(serialized_event)
