from abc import abstractmethod
from typing import Type, get_type_hints

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware import EventMiddleware
from bus_station.event_terminal.middleware.event_middleware_executor import EventMiddlewareExecutor
from bus_station.shared_terminal.bus import Bus


class EventBus(Bus[EventConsumer, EventMiddleware]):
    def __init__(self):
        super().__init__(EventMiddlewareExecutor)

    def _get_consumer_event(self, consumer: EventConsumer) -> Type[Event]:
        consume_typing = get_type_hints(consumer.consume)

        if "event" not in consume_typing:
            raise TypeError(f"Consume event not found for {consumer.__class__.__name__}")

        if not issubclass(consume_typing["event"], Event):
            raise TypeError(f"Wrong type for consume event of {consumer.__class__.__name__}")

        return consume_typing["event"]

    @abstractmethod
    def publish(self, event: Event) -> None:
        pass
