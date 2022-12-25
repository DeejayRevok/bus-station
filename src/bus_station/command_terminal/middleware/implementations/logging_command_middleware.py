from logging import Logger
from typing import Optional

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware import CommandMiddleware


class LoggingCommandMiddleware(CommandMiddleware):
    def __init__(self, logger: Logger):
        self.__logger = logger

    def before_handle(self, passenger: Command, bus_stop: CommandHandler) -> None:
        self.__logger.info(f"Starting handling command {passenger} with {bus_stop.bus_stop_name()}")

    def after_handle(
        self, passenger: Command, bus_stop: CommandHandler, handling_exception: Optional[Exception] = None
    ) -> None:
        if handling_exception is not None:
            self.__logger.exception(
                handling_exception,
                exc_info=(handling_exception.__class__, handling_exception, handling_exception.__traceback__),
            )
        self.__logger.info(f"Finished handling command {passenger} with {bus_stop.bus_stop_name()}")
