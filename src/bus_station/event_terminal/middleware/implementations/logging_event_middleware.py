from logging import Logger
from typing import Optional

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware import EventMiddleware


class LoggingEventMiddleware(EventMiddleware):
    def __init__(self, logger: Logger):
        self.__logger = logger

    def before_consume(self, passenger: Event, bus_stop: EventConsumer) -> None:
        self.__logger.info(f"Starting consuming event {passenger} with {bus_stop.__class__.__name__}")

    def after_consume(
        self, passenger: Event, bus_stop: EventConsumer, consume_exception: Optional[Exception] = None
    ) -> None:
        if consume_exception is not None:
            self.__logger.exception(consume_exception)
        self.__logger.info(f"Finished consuming event {passenger} with {bus_stop.__class__.__name__}")
