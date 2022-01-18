from threading import Thread
from typing import final

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry


@final
class ThreadedEventBus(EventBus):
    def __init__(self, event_registry: InMemoryRegistry):
        super().__init__()
        self.__event_registry = event_registry

    def register(self, handler: EventConsumer) -> None:
        consumer_event = self._get_consumer_event(handler)
        event_consumers = self.__event_registry.get_passenger_destination(consumer_event)
        if event_consumers is not None:
            event_consumers.append(handler)
        else:
            self.__event_registry.register(consumer_event, [handler])

    def publish(self, event: Event) -> None:
        event_consumers = self.__event_registry.get_passenger_destination(event.__class__)
        if event_consumers is not None:
            for event_consumer in event_consumers:
                execution_thread = Thread(target=self._middleware_executor.execute, args=(event, event_consumer))
                execution_thread.start()
