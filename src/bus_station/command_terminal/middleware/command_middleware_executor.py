from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware import CommandMiddleware
from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor


class CommandMiddlewareExecutor(PassengerMiddlewareExecutor[Command, CommandMiddleware, CommandHandler]):
    def execute(self, passenger: Command, passenger_bus_stop: CommandHandler) -> None:
        middlewares = list(self._get_middlewares())
        for middleware in middlewares:
            middleware.before_handle(passenger, passenger_bus_stop)

        passenger_bus_stop.handle(passenger)

        for middleware in reversed(middlewares):
            middleware.after_handle(passenger, passenger_bus_stop)
