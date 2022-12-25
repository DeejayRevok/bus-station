import time
from logging import Logger
from typing import Optional

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware import EventMiddleware


class TimingEventMiddleware(EventMiddleware):
    def __init__(self, logger: Logger):
        self.__logger = logger
        self.__start_time = None

    def before_consume(self, passenger: Event, bus_stop: EventConsumer) -> None:
        self.__start_time = time.time()

    def after_consume(
        self, passenger: Event, bus_stop: EventConsumer, consume_exception: Optional[Exception] = None
    ) -> None:
        execution_time = time.time() - self.__start_time
        execution_result_hint = "successfully" if consume_exception is None else "wrongly"
        self.__logger.info(
            f"Event {passenger} consumed {execution_result_hint} "
            f"by {bus_stop.bus_stop_name()} in {execution_time} seconds"
        )
