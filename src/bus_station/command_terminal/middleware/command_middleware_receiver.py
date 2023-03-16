from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware import CommandMiddleware
from bus_station.passengers.reception.passenger_middleware_receiver import PassengerMiddlewareReceiver


class CommandMiddlewareReceiver(PassengerMiddlewareReceiver[Command, CommandHandler, CommandMiddleware]):
    def _receive(self, passenger: Command, passenger_bus_stop: CommandHandler) -> None:
        middlewares = list(self._get_middlewares())
        for middleware in middlewares:
            middleware.before_handle(passenger, passenger_bus_stop)

        handling_exception = None
        try:
            passenger_bus_stop.handle(passenger)
        except Exception as ex:
            handling_exception = ex

        for middleware in reversed(middlewares):
            middleware.after_handle(passenger, passenger_bus_stop, handling_exception=handling_exception)

        if handling_exception is not None:
            raise handling_exception
