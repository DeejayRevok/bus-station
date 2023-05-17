from functools import partial
from typing import List, Optional, Set

from bus_station.bus_stop.registration.bus_stop_registry import BusStopRegistry
from bus_station.bus_stop.registration.supervisor.bus_stop_registration_supervisor import BusStopRegistrationSupervisor
from bus_station.bus_stop.resolvers.bus_stop_resolver import BusStopResolver
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.passengers.passenger_registry import passenger_bus_stop_registry
from bus_station.passengers.passenger_resolvers import resolve_passenger_class_from_bus_stop


class EventConsumerRegistry(BusStopRegistry[EventConsumer]):
    def __init__(
        self,
        bus_stop_resolver: BusStopResolver,
        registration_supervisors: Optional[List[BusStopRegistrationSupervisor]] = None,
    ):
        bus_stop_passenger_resolver = partial(
            resolve_passenger_class_from_bus_stop,
            bus_stop_handle_function_name="consume",
            passenger_type_name="event",
        )
        super().__init__(bus_stop_resolver, bus_stop_passenger_resolver, registration_supervisors)

    def get_consumers_from_event(self, event_name: str) -> Set[EventConsumer]:
        result_set = set()
        for event_consumer_id in passenger_bus_stop_registry.get_bus_stops_for_passenger(event_name):
            result_set.add(self._bus_stop_resolver.resolve(event_consumer_id))
        return result_set
