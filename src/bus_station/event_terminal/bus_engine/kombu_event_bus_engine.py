from typing import ClassVar

from kombu import Connection, Exchange, Queue
from kombu.transport.base import StdChannel

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.event_consumer_not_found import EventConsumerNotFound
from bus_station.event_terminal.event_consumer_registry import EventConsumerRegistry
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.engine.engine import Engine


class KombuEventBusEngine(Engine):
    __DEAD_LETTER_EXCHANGE_NAME: ClassVar = "failed_events"

    def __init__(
        self,
        broker_connection: Connection,
        event_receiver: PassengerReceiver[Event, EventConsumer],
        event_consumer_registry: EventConsumerRegistry,
        event_deserializer: PassengerDeserializer,
        event_consumer_name: str,
    ):
        event_consumer = event_consumer_registry.get_bus_stop_by_name(event_consumer_name)
        if event_consumer is None:
            raise EventConsumerNotFound(event_consumer_name)

        event = event_consumer.passenger()

        channel = broker_connection.channel()
        self.__create_dead_letter_exchange(channel)

        event_exchange = self.__create_event_consumer_exchange(event.passenger_name(), channel)
        event_consumer_queue = self.__create_event_consumer_queue(event_consumer, event_exchange, channel)

        self.__event_consumer_consumer = PassengerKombuConsumer(
            broker_connection,
            event_consumer_queue,
            event_consumer,
            event,
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

    def __create_dead_letter_exchange(self, channel: StdChannel) -> None:
        command_failure_exchange = Exchange(self.__DEAD_LETTER_EXCHANGE_NAME, type="fanout", channel=channel)
        command_failure_exchange.declare()

    def __create_event_consumer_exchange(self, event_name: str, broker_channel: StdChannel) -> Exchange:
        event_exchange = Exchange(event_name, type="fanout")
        event_exchange.declare(channel=broker_channel)
        return event_exchange

    def __create_event_consumer_queue(
        self, event_consumer: EventConsumer, event_exchange: Exchange, broker_channel: StdChannel
    ) -> Queue:
        consumer_queue = Queue(
            name=event_consumer.bus_stop_name(),
            exchange=event_exchange,
            queue_arguments={"x-dead-letter-exchange": self.__DEAD_LETTER_EXCHANGE_NAME},
        )
        consumer_queue.declare(channel=broker_channel)
        return consumer_queue
