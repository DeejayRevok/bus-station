import time
from logging import Logger
from typing import Optional

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware import CommandMiddleware


class TimingCommandMiddleware(CommandMiddleware):
    def __init__(self, logger: Logger):
        self.__logger = logger
        self.__start_time = None

    def before_handle(self, passenger: Command, bus_stop: CommandHandler) -> None:
        self.__start_time = time.time()

    def after_handle(
        self, passenger: Command, bus_stop: CommandHandler, handling_exception: Optional[Exception] = None
    ) -> None:
        execution_time = time.time() - self.__start_time
        execution_result_hint = "successfully" if handling_exception is None else "wrongly"
        self.__logger.info(
            f"Command {passenger} handled {execution_result_hint} "
            f"by {bus_stop.bus_stop_name()} in {execution_time} seconds"
        )
