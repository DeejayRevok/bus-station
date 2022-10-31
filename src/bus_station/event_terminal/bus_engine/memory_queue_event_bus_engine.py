from typing import TypeVar

from bus_station.event_terminal.contact_not_found_for_consumer import ContactNotFoundForConsumer
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.event_registry import EventRegistry
from bus_station.passengers.memory_queue_passenger_worker import MemoryQueuePassengerWorker
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.engine.engine import Engine

E = TypeVar("E", bound=Event)


class MemoryQueueEventBusEngine(Engine):
    def __init__(
        self,
        event_registry: EventRegistry,
        event_receiver: PassengerReceiver[Event, EventConsumer],
        event_deserializer: PassengerDeserializer,
        event_consumer: EventConsumer,
    ):
        super().__init__()
        event_queue = event_registry.get_event_destination_contact(event_consumer)
        if event_queue is None:
            raise ContactNotFoundForConsumer(event_consumer.__class__.__name__)

        self.__event_worker = MemoryQueuePassengerWorker(
            event_queue, event_consumer, event_receiver, event_deserializer
        )

    def start(self) -> None:
        try:
            self.__event_worker.work()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        self.__event_worker.stop()
