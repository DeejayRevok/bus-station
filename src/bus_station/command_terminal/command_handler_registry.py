from functools import partial
from typing import List, Optional

from bus_station.bus_stop.registration.bus_stop_registry import BusStopRegistry
from bus_station.bus_stop.registration.supervisor.bus_stop_registration_supervisor import BusStopRegistrationSupervisor
from bus_station.bus_stop.resolvers.bus_stop_resolver import BusStopResolver
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.passengers.passenger_registry import passenger_bus_stop_registry
from bus_station.passengers.passenger_resolvers import resolve_passenger_class_from_bus_stop


class CommandHandlerRegistry(BusStopRegistry[CommandHandler]):
    def __init__(
        self,
        bus_stop_resolver: BusStopResolver,
        registration_supervisors: Optional[List[BusStopRegistrationSupervisor]] = None,
    ):
        bus_stop_passenger_resolver = partial(
            resolve_passenger_class_from_bus_stop,
            bus_stop_handle_function_name="handle",
            passenger_type_name="command",
        )
        super().__init__(bus_stop_resolver, bus_stop_passenger_resolver, registration_supervisors)

    def get_handler_from_command(self, command_name: str) -> Optional[CommandHandler]:
        command_handler_ids = passenger_bus_stop_registry.get_bus_stops_for_passenger(command_name)
        if len(command_handler_ids) == 0:
            return None

        command_handler_id = next(iter(command_handler_ids))
        return self._bus_stop_resolver.resolve(command_handler_id)
