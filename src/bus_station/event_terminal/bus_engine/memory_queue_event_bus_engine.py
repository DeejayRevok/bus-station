from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.event_consumer_not_found import EventConsumerNotFound
from bus_station.event_terminal.event_consumer_registry import EventConsumerRegistry
from bus_station.passengers.memory_queue_passenger_worker import MemoryQueuePassengerWorker
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.engine.engine import Engine
from bus_station.shared_terminal.factories.memory_queue_factory import memory_queue_factory


class MemoryQueueEventBusEngine(Engine):
    def __init__(
        self,
        event_consumer_registry: EventConsumerRegistry,
        event_receiver: PassengerReceiver[Event, EventConsumer],
        event_deserializer: PassengerDeserializer,
        event_consumer_name: str,
    ):
        event_consumer = event_consumer_registry.get_bus_stop_by_name(event_consumer_name)
        if event_consumer is None:
            raise EventConsumerNotFound(event_consumer_name)

        event_queue = memory_queue_factory.queue_with_id(event_consumer.bus_stop_name())

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
