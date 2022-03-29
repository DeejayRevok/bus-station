from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry


class SyncEventBus(EventBus):
    def __init__(self, event_registry: InMemoryEventRegistry):
        super().__init__()
        self.__event_registry = event_registry

    def publish(self, event: Event) -> None:
        event_consumers = self.__event_registry.get_event_destination_contacts(event.__class__)
        if event_consumers is None:
            return

        for event_consumer in event_consumers:
            self._middleware_executor.execute(event, event_consumer)
