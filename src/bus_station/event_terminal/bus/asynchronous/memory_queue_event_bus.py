from multiprocessing import Queue

from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer_registry import EventConsumerRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.factories.memory_queue_factory import memory_queue_factory


class MemoryQueueEventBus(EventBus):
    def __init__(
        self,
        event_serializer: PassengerSerializer,
        event_consumer_registry: EventConsumerRegistry,
    ):
        self.__event_serializer = event_serializer
        self.__event_consumer_registry = event_consumer_registry

    def _transport(self, passenger: Event) -> None:
        for event_consumer in self.__event_consumer_registry.get_consumers_from_event(passenger.passenger_name()):
            event_consumer_queue = memory_queue_factory.queue_with_id(event_consumer.bus_stop_name())
            self.__put_event(event_consumer_queue, passenger)

    def __put_event(self, queue: Queue, event: Event) -> None:
        serialized_event = self.__event_serializer.serialize(event)
        queue.put(serialized_event)
