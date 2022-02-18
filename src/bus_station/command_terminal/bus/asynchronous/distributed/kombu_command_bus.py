from multiprocessing import Process
from typing import ClassVar, List, Optional, Tuple, Type

from kombu import Connection
from kombu.messaging import Exchange, Producer, Queue
from kombu.transport.virtual import Channel

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.passenger import Passenger
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.bus_stop import BusStop
from bus_station.shared_terminal.runnable import Runnable, is_running


class KombuCommandBus(CommandBus, Runnable):
    __DEAD_LETTER_EXCHANGE_NAME: ClassVar[str] = "failed_commands"

    def __init__(
        self,
        broker_connection: Connection,
        command_serializer: PassengerSerializer,
        command_deserializer: PassengerDeserializer,
        command_registry: RemoteCommandRegistry,
    ):
        CommandBus.__init__(self)
        Runnable.__init__(self)
        self.__broker_connection = broker_connection
        self.__command_consumers: List[PassengerKombuConsumer] = list()
        self.__command_consumer_processes: List[Process] = list()
        self.__command_serializer = command_serializer
        self.__command_deserializer = command_deserializer
        self.__command_registry = command_registry
        self.__producer: Optional[Producer] = None

    def _start(self) -> None:
        broker_channel = self.__broker_connection.channel()
        self.__create_dead_letter_exchange(broker_channel)

        for command in self.__command_registry.get_registered_passengers():
            command_handler_registration = self.__command_registry.get_passenger_destination_registration(command)
            if command_handler_registration is None:
                continue

            try:
                consumer, consumer_process, consumer_queue = self.__create_consumer(command_handler_registration.destination, command)
            except Exception as ex:
                self.__command_registry.unregister(command)
                raise ex

            self.__command_consumers.append(consumer)
            self.__command_consumer_processes.append(consumer_process)
            consumer_queue.declare(channel=broker_channel)
            consumer_process.start()

        self.__producer = Producer(broker_channel)

    def __create_dead_letter_exchange(self, channel: Channel) -> None:
        command_failure_exchange = Exchange(self.__DEAD_LETTER_EXCHANGE_NAME, type="fanout", channel=channel)
        command_failure_exchange.declare()

    def __create_consumer(
        self, command_handler: BusStop, command_cls: Type[Passenger]
    ) -> Tuple[PassengerKombuConsumer, Process, Queue]:
        handler_queue = Queue(
            command_cls.__name__, queue_arguments={"x-dead-letter-exchange": self.__DEAD_LETTER_EXCHANGE_NAME}
        )
        handler_consumer = PassengerKombuConsumer(
            self.__broker_connection,
            handler_queue,
            command_handler,
            command_cls,
            self._middleware_executor,
            self.__command_deserializer,
        )
        handler_process = Process(target=handler_consumer.run)
        return handler_consumer, handler_process, handler_queue

    @is_running
    def execute(self, command: Command) -> None:
        command_handler_registration = self.__command_registry.get_passenger_destination_registration(command.__class__)
        if command_handler_registration is None or command_handler_registration.destination_contact is None:
            raise HandlerNotFoundForCommand(command.__class__.__name__)

        self.__publish_command(command, command_handler_registration.destination_contact)

    def __publish_command(self, command: Command, routing_key: str) -> None:
        serialized_command = self.__command_serializer.serialize(command)
        if self.__producer is not None:
            self.__producer.publish(
                serialized_command,
                exchange="",
                routing_key=routing_key,
                retry=True,
                retry_policy={
                    "interval_start": 0,
                    "interval_step": 2,
                    "interval_max": 10,
                    "max_retries": 10,
                },
            )

    def _stop(self) -> None:
        for consumer in self.__command_consumers:
            consumer.stop()
        for process in self.__command_consumer_processes:
            process.join()
        if self.__producer is not None:
            self.__producer.release()
        self.__broker_connection.release()
