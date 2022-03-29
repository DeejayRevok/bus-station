import time
from logging import Logger

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware import EventMiddleware


class TimingEventMiddleware(EventMiddleware):
    def __init__(self, logger: Logger):
        self.__logger = logger
        self.__start_time = None

    def before_consume(self, passenger: Event, bus_stop: EventConsumer) -> None:
        self.__start_time = time.time()

    def after_consume(self, passenger: Event, bus_stop: EventConsumer) -> None:
        execution_time = time.time() - self.__start_time
        self.__logger.info(f"Event {passenger} consumed by {bus_stop.__class__.__name__} in {execution_time} seconds")
