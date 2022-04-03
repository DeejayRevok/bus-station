from multiprocessing import Process
from typing import ClassVar, List, NoReturn, Optional, Tuple, Type

from kombu import Connection
from kombu.messaging import Exchange, Producer, Queue
from kombu.transport.virtual import Channel

from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.remote_event_registry import RemoteEventRegistry
from bus_station.passengers.passenger import Passenger
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.bus_stop import BusStop
from bus_station.shared_terminal.runnable import Runnable


class KombuEventBus(EventBus, Runnable):
    __DEAD_LETTER_EXCHANGE_NAME: ClassVar[str] = "failed_events"

    def __init__(
        self,
        broker_connection: Connection,
        event_serializer: PassengerSerializer,
        event_deserializer: PassengerDeserializer,
        event_registry: RemoteEventRegistry,
        event_receiver: PassengerReceiver[Event, EventConsumer],
    ):
        EventBus.__init__(self, event_receiver)
        Runnable.__init__(self)
        self.__broker_connection = broker_connection
        self.__event_kombu_consumers: List[PassengerKombuConsumer] = []
        self.__event_kombu_consumer_processes: List[Process] = []
        self.__event_serializer = event_serializer
        self.__event_deserializer = event_deserializer
        self.__event_registry = event_registry
        self.__producer: Optional[Producer] = None

    def _start(self) -> None:
        broker_channel = self.__broker_connection.channel()
        self.__create_dead_letter_exchange(broker_channel)

        for event in self.__event_registry.get_events_registered():
            event_consumers = self.__event_registry.get_event_destinations(event)
            exchange_names = self.__event_registry.get_event_destination_contacts(event)
            if event_consumers is None or exchange_names is None:
                continue
            for event_consumer, event_exchange_name in zip(event_consumers, exchange_names):
                event_exchange = self.__create_event_exchange(event_exchange_name)
                event_exchange.declare(channel=broker_channel)
                kombu_consumer, kombu_consumer_process, kombu_queue = self.__create_consumer(
                    event_consumer, event, event_exchange
                )
                kombu_queue.declare(channel=broker_channel)
                kombu_consumer_process.start()
                self.__event_kombu_consumers.append(kombu_consumer)
                self.__event_kombu_consumer_processes.append(kombu_consumer_process)

        self.__producer = Producer(broker_channel)

    def __create_dead_letter_exchange(self, channel: Channel) -> None:
        event_failure_exchange = Exchange(self.__DEAD_LETTER_EXCHANGE_NAME, type="fanout", channel=channel)
        event_failure_exchange.declare()

    def __create_event_exchange(self, event_name: str) -> Exchange:
        event_exchange = Exchange(event_name, type="fanout")
        return event_exchange

    def __create_consumer(
        self, event_consumer: BusStop, event_cls: Type[Passenger], exchange: Exchange
    ) -> Tuple[PassengerKombuConsumer, Process, Queue]:
        consumer_queue = Queue(
            event_consumer.__class__.__name__,
            exchange=exchange,
            queue_arguments={"x-dead-letter-exchange": self.__DEAD_LETTER_EXCHANGE_NAME},
        )
        consumer_consumer = PassengerKombuConsumer(
            self.__broker_connection,
            consumer_queue,
            event_consumer,
            event_cls,
            self._event_receiver,
            self.__event_deserializer,
        )
        consumer_process = Process(target=consumer_consumer.run)
        return consumer_consumer, consumer_process, consumer_queue

    def transport(self, passenger: Event) -> NoReturn:
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

    def _stop(self) -> None:
        for kombu_consumer in self.__event_kombu_consumers:
            kombu_consumer.stop()
        for kombu_consumer_process in self.__event_kombu_consumer_processes:
            kombu_consumer_process.join()
        if self.__producer is not None:
            self.__producer.release()
        self.__broker_connection.release()
