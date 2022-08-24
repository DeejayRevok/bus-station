from kombu import Connection
from kombu.messaging import Producer

from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.registry.remote_event_registry import RemoteEventRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class KombuEventBus(EventBus):
    def __init__(
        self,
        broker_connection: Connection,
        event_serializer: PassengerSerializer,
        event_registry: RemoteEventRegistry,
    ):
        self.__broker_connection = broker_connection
        self.__event_serializer = event_serializer
        self.__event_registry = event_registry
        self.__producer = Producer(broker_connection.channel())

    def transport(self, passenger: Event) -> None:
        event_exchange_names = self.__event_registry.get_event_destination_contacts(passenger.__class__)
        if event_exchange_names is None:
            return

        published_exchanges = []
        for event_exchange_name in event_exchange_names:
            if event_exchange_name in published_exchanges:
                continue
            self.__publish_event(passenger, event_exchange_name)
            published_exchanges.append(event_exchange_name)

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

    def shutdown(self) -> None:
        self.__producer.release()
