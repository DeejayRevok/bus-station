import time
from logging import Logger

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware import CommandMiddleware


class TimingCommandMiddleware(CommandMiddleware):
    def __init__(self, logger: Logger):
        self.__logger = logger
        self.__start_time = None

    def before_handle(self, passenger: Command, bus_stop: CommandHandler) -> None:
        self.__start_time = time.time()

    def after_handle(self, passenger: Command, bus_stop: CommandHandler) -> None:
        execution_time = time.time() - self.__start_time
        self.__logger.info(f"Command {passenger} handled by {bus_stop.__class__.__name__} in {execution_time} seconds")
