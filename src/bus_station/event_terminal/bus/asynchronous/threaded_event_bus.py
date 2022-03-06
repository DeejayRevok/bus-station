from threading import Thread

from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry


class ThreadedEventBus(EventBus):
    def __init__(self, event_registry: InMemoryEventRegistry):
        super().__init__()
        self.__event_registry = event_registry

    def publish(self, event: Event) -> None:
        event_consumers = self.__event_registry.get_event_destinations(event.__class__)
        if event_consumers is None:
            return

        for event_consumer in event_consumers:
            execution_thread = Thread(target=self._middleware_executor.execute, args=(event, event_consumer))
            execution_thread.start()
