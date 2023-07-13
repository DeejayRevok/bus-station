from typing import Set

from bus_station.bus_stop.registration.bus_stop_registry import BusStopRegistry
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.passengers.passenger_registry import passenger_bus_stop_registry


class EventConsumerRegistry(BusStopRegistry[EventConsumer]):
    def get_consumers_from_event(self, event_name: str) -> Set[EventConsumer]:
        result_set = set()
        for event_consumer_name in passenger_bus_stop_registry.get_bus_stops_for_passenger(event_name):
            event_consumer = self.get_bus_stop_by_name(event_consumer_name)
            if isinstance(event_consumer, EventConsumer) is True:
                result_set.add(event_consumer)
        return result_set
