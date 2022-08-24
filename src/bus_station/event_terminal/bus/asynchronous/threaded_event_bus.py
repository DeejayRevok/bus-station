from threading import Thread

from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver


class ThreadedEventBus(EventBus):
    def __init__(self, event_registry: InMemoryEventRegistry, event_receiver: PassengerReceiver[Event, EventConsumer]):
        self.__event_receiver = event_receiver
        self.__event_registry = event_registry

    def transport(self, passenger: Event) -> None:
        event_consumers = self.__event_registry.get_event_destination_contacts(passenger.__class__)
        if event_consumers is None:
            return

        for event_consumer in event_consumers:
            execution_thread = Thread(target=self.__event_receiver.receive, args=(passenger, event_consumer))
            execution_thread.start()
