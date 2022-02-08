from multiprocessing import Process
from typing import ClassVar, List, Optional, Tuple, Type

from kombu import Connection
from kombu.messaging import Exchange, Producer, Queue
from kombu.transport.virtual import Channel

from bus_station.event_terminal.bus.event_bus import EventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.runnable import Runnable, is_not_running, is_running


class KombuEventBus(EventBus, Runnable):
    __DEAD_LETTER_EXCHANGE_NAME: ClassVar[str] = "failed_events"

    def __init__(
        self,
        broker_connection: Connection,
        event_serializer: PassengerSerializer,
        event_deserializer: PassengerDeserializer,
    ):
        EventBus.__init__(self)
        Runnable.__init__(self)
        self.__broker_connection = broker_connection
        self.__event_kombu_consumers: List[PassengerKombuConsumer] = list()
        self.__event_kombu_consumer_processes: List[Process] = list()
        self.__event_queues: List[Queue] = list()
        self.__event_exchanges: List[Exchange] = list()
        self.__event_serializer = event_serializer
        self.__event_deserializer = event_deserializer
        self.__producer: Optional[Producer] = None

    def _start(self) -> None:
        broker_channel = self.__broker_connection.channel()
        self.__create_dead_letter_exchange(broker_channel)
        for exchange in self.__event_exchanges:
            exchange.declare(channel=broker_channel)
        for queue in self.__event_queues:
            queue.declare(channel=broker_channel)
        for process in self.__event_kombu_consumer_processes:
            process.start()
        self.__producer = Producer(broker_channel)

    def __create_dead_letter_exchange(self, channel: Channel) -> None:
        event_failure_exchange = Exchange(self.__DEAD_LETTER_EXCHANGE_NAME, type="fanout", channel=channel)
        event_failure_exchange.declare()

    @is_not_running
    def register(self, handler: EventConsumer) -> None:
        consumer_event = self._get_consumer_event(handler)
        event_exchange = self.__create_event_exchange(consumer_event.__name__)
        self.__event_exchanges.append(event_exchange)
        kombu_consumer, kombu_consumer_process = self.__create_consumer(handler, consumer_event, event_exchange)
        self.__event_kombu_consumers.append(kombu_consumer)
        self.__event_kombu_consumer_processes.append(kombu_consumer_process)

    def __create_event_exchange(self, event_name: str) -> Exchange:
        event_exchange = Exchange(event_name, type="fanout")
        return event_exchange

    def __create_consumer(
        self, event_consumer: EventConsumer, event_cls: Type[Event], exchange: Exchange
    ) -> Tuple[PassengerKombuConsumer, Process]:
        consumer_queue = Queue(
            event_consumer.__class__.__name__,
            exchange=exchange,
            queue_arguments={"x-dead-letter-exchange": self.__DEAD_LETTER_EXCHANGE_NAME},
        )
        self.__event_queues.append(consumer_queue)
        consumer_consumer = PassengerKombuConsumer(
            self.__broker_connection,
            consumer_queue,
            event_consumer,
            event_cls,
            self._middleware_executor,
            self.__event_deserializer,
        )
        consumer_process = Process(target=consumer_consumer.run)
        return consumer_consumer, consumer_process

    @is_running
    def publish(self, event: Event) -> None:
        self.__publish_event(event)

    def __publish_event(self, event: Event) -> None:
        serialized_event = self.__event_serializer.serialize(event)
        if self.__producer is not None:
            self.__producer.publish(
                serialized_event,
                exchange=event.__class__.__name__,
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
