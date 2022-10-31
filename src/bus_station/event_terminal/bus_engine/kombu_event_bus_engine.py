from typing import ClassVar, TypeVar

from kombu import Connection
from kombu.messaging import Exchange, Queue
from kombu.transport.virtual import Channel

from bus_station.event_terminal.contact_not_found_for_consumer import ContactNotFoundForConsumer
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.remote_event_registry import RemoteEventRegistry
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.engine.engine import Engine

E = TypeVar("E", bound=Event)


class KombuEventBusEngine(Engine):
    __DEAD_LETTER_EXCHANGE_NAME: ClassVar = "failed_events"

    def __init__(
        self,
        broker_connection: Connection,
        event_registry: RemoteEventRegistry,
        event_receiver: PassengerReceiver[Event, EventConsumer],
        event_deserializer: PassengerDeserializer,
        event_consumer: EventConsumer,
    ):
        super().__init__()
        event_exchange_name = event_registry.get_event_destination_contact(event_consumer)
        if event_exchange_name is None:
            raise ContactNotFoundForConsumer(event_consumer.__class__.__name__)

        broker_connection = broker_connection
        channel = broker_connection.channel()
        self.__create_dead_letter_exchange(channel)

        event_exchange = self.__create_event_consumer_exchange(event_exchange_name, channel)
        event_consumer_queue = self.__create_event_consumer_queue(event_consumer, event_exchange, channel)

        self.__event_consumer_consumer = PassengerKombuConsumer(
            broker_connection,
            event_consumer_queue,
            event_consumer,
            event_registry.get_consumer_event(event_consumer),
            event_receiver,
            event_deserializer,
        )

    def start(self) -> None:
        try:
            self.__event_consumer_consumer.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        self.__event_consumer_consumer.stop()

    def __create_dead_letter_exchange(self, channel: Channel) -> None:
        command_failure_exchange = Exchange(self.__DEAD_LETTER_EXCHANGE_NAME, type="fanout", channel=channel)
        command_failure_exchange.declare()

    def __create_event_consumer_exchange(self, event_name: str, broker_channel: Channel) -> Exchange:
        event_exchange = Exchange(event_name, type="fanout")
        event_exchange.declare(channel=broker_channel)
        return event_exchange

    def __create_event_consumer_queue(
        self, event_consumer: EventConsumer, event_exchange: Exchange, broker_channel: Channel
    ) -> Queue:
        consumer_queue = Queue(
            name=event_consumer.__class__.__name__,
            exchange=event_exchange,
            queue_arguments={"x-dead-letter-exchange": self.__DEAD_LETTER_EXCHANGE_NAME},
        )
        consumer_queue.declare(channel=broker_channel)
        return consumer_queue
