from typing import Optional

from bus_station.bus_stop.registration.bus_stop_registry import BusStopRegistry
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.passengers.passenger_registry import passenger_bus_stop_registry


class CommandHandlerRegistry(BusStopRegistry[CommandHandler]):
    def get_handler_from_command(self, command_name: str) -> Optional[CommandHandler]:
        command_handler_ids = passenger_bus_stop_registry.get_bus_stops_for_passenger(command_name)
        if len(command_handler_ids) == 0:
            return None

        command_handler_id = next(iter(command_handler_ids))
        resolved_command_handler = self._bus_stop_resolver.resolve(command_handler_id)

        if not isinstance(resolved_command_handler, CommandHandler):
            raise HandlerNotFoundForCommand(command_name)
        return resolved_command_handler
