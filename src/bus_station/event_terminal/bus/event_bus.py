from abc import abstractmethod

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.middleware.event_middleware import EventMiddleware
from bus_station.event_terminal.middleware.event_middleware_executor import EventMiddlewareExecutor
from bus_station.shared_terminal.bus import Bus


class EventBus(Bus[EventMiddleware]):
    def __init__(self):
        super().__init__(EventMiddlewareExecutor)

    @abstractmethod
    def publish(self, event: Event) -> None:
        pass
