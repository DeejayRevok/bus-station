from kombu import Connection, Producer

from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event import Event
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class KombuEventBus(EventBus):
    def __init__(
        self,
        broker_connection: Connection,
        event_serializer: PassengerSerializer,
    ):
        self.__broker_connection = broker_connection
        self.__event_serializer = event_serializer
        self.__producer = Producer(broker_connection.channel())

    def _transport(self, passenger: Event) -> None:
        self.__publish_event(passenger, passenger.passenger_name())

    def __publish_event(self, event: Event, event_exchange_name: str) -> None:
        serialized_event = self.__event_serializer.serialize(event)
        if self.__producer is not None:
            self.__producer.publish(
                serialized_event,
                exchange=event_exchange_name,
                retry=True,
                retry_policy={
                    "interval_start": 0,
                    "interval_step": 2,
                    "interval_max": 10,
                    "max_retries": 10,
                },
            )
