from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.event_consumer_registry import EventConsumerRegistry
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver


class SyncEventBus(EventBus):
    def __init__(
        self, event_consumer_registry: EventConsumerRegistry, event_receiver: PassengerReceiver[Event, EventConsumer]
    ):
        self.__event_receiver = event_receiver
        self.__event_consumer_registry = event_consumer_registry

    def _transport(self, passenger: Event) -> None:
        for event_consumer in self.__event_consumer_registry.get_consumers_from_event(passenger.passenger_name()):
            self.__event_receiver.receive(passenger, event_consumer)
