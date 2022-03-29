from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware import CommandMiddleware
from bus_station.tracking_terminal.trackers.passenger_tracker import PassengerTracker


class TrackingCommandMiddleware(CommandMiddleware):
    def __init__(self, passenger_tracker: PassengerTracker):
        self.__tracker = passenger_tracker

    def before_handle(self, passenger: Command, bus_stop: CommandHandler) -> None:
        self.__tracker.start_tracking(passenger, bus_stop)

    def after_handle(self, passenger: Command, bus_stop: CommandHandler) -> None:
        self.__tracker.end_tracking(passenger)
