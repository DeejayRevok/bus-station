from multiprocessing import Process
from typing import ClassVar, List, Optional, Tuple, Type

from kombu import Connection
from kombu.messaging import Exchange, Producer, Queue
from kombu.transport.virtual import Channel

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.runnable import Runnable


class KombuCommandBus(CommandBus, Runnable):
    __DEAD_LETTER_EXCHANGE_NAME: ClassVar[str] = "failed_commands"

    def __init__(
        self,
        broker_connection: Connection,
        command_serializer: PassengerSerializer,
        command_deserializer: PassengerDeserializer,
        command_registry: RemoteCommandRegistry,
        command_receiver: PassengerReceiver[Command, CommandHandler],
    ):
        CommandBus.__init__(self, command_receiver)
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

        for command in self.__command_registry.get_commands_registered():
            handler = self.__command_registry.get_command_destination(command)
            handler_queue_name = self.__command_registry.get_command_destination_contact(command)
            if handler_queue_name is None or handler is None:
                continue
            consumer, consumer_process, consumer_queue = self.__create_consumer(handler, handler_queue_name, command)
            self.__command_consumers.append(consumer)
            self.__command_consumer_processes.append(consumer_process)
            consumer_queue.declare(channel=broker_channel)
            consumer_process.start()

        self.__producer = Producer(broker_channel)

    def __create_dead_letter_exchange(self, channel: Channel) -> None:
        command_failure_exchange = Exchange(self.__DEAD_LETTER_EXCHANGE_NAME, type="fanout", channel=channel)
        command_failure_exchange.declare()

    def __create_consumer(
        self, command_handler: CommandHandler, handler_queue_name: str, command_cls: Type[Command]
    ) -> Tuple[PassengerKombuConsumer, Process, Queue]:
        handler_queue = Queue(
            handler_queue_name, queue_arguments={"x-dead-letter-exchange": self.__DEAD_LETTER_EXCHANGE_NAME}
        )
        handler_consumer = PassengerKombuConsumer(
            self.__broker_connection,
            handler_queue,
            command_handler,
            command_cls,
            self._command_receiver,
            self.__command_deserializer,
        )
        handler_process = Process(target=handler_consumer.run)
        return handler_consumer, handler_process, handler_queue

    def transport(self, passenger: Command) -> None:
        handler_queue_name = self.__command_registry.get_command_destination_contact(passenger.__class__)
        if handler_queue_name is None:
            raise HandlerNotFoundForCommand(passenger.__class__.__name__)

        self.__publish_command(passenger, handler_queue_name)

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
