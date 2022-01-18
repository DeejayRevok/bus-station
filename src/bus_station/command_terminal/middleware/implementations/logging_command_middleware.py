from logging import Logger

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware import CommandMiddleware


class LoggingCommandMiddleware(CommandMiddleware):
    def __init__(self, logger: Logger):
        self.__logger = logger

    def before_handle(self, passenger: Command, bus_stop: CommandHandler) -> None:
        self.__logger.info(f"Starting handling command {passenger} with {bus_stop.__class__.__name__}")

    def after_handle(self, passenger: Command, bus_stop: CommandHandler) -> None:
        self.__logger.info(f"Finished handling command {passenger} with {bus_stop.__class__.__name__}")
