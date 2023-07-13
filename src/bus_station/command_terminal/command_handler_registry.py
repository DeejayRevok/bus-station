from typing import Optional

from bus_station.bus_stop.registration.bus_stop_registry import BusStopRegistry
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.passengers.passenger_registry import passenger_bus_stop_registry


class CommandHandlerRegistry(BusStopRegistry[CommandHandler]):
    def get_handler_from_command(self, command_name: str) -> Optional[CommandHandler]:
        command_handler_names = passenger_bus_stop_registry.get_bus_stops_for_passenger(command_name)
        if len(command_handler_names) == 0:
            return None

        command_handler_name = next(iter(command_handler_names))
        command_handler = self.get_bus_stop_by_name(command_handler_name)

        if not isinstance(command_handler, CommandHandler):
            raise HandlerNotFoundForCommand(command_name)

        return command_handler
