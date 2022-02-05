from multiprocessing import Process
from typing import Tuple, final, ClassVar, Type, List, TypeVar, Optional

from kombu import Connection
from kombu.messaging import Producer, Queue, Exchange
from kombu.transport.virtual import Channel

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_for_command_already_registered import (
    HandlerForCommandAlreadyRegistered,
)
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.registry.remote_registry import RemoteRegistry
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.runnable import Runnable, is_not_running, is_running

R = TypeVar("R", bound=RemoteRegistry)


@final
class KombuCommandBus(CommandBus, Runnable):
    __DEAD_LETTER_EXCHANGE_NAME: ClassVar[str] = "failed_commands"

    def __init__(
        self,
        broker_connection: Connection,
        command_serializer: PassengerSerializer,
        command_deserializer: PassengerDeserializer,
        command_registry: R,
    ):
        CommandBus.__init__(self)
        Runnable.__init__(self)
        self.__broker_connection = broker_connection
        self.__command_consumers: List[PassengerKombuConsumer] = list()
        self.__command_consumer_processes: List[Process] = list()
        self.__command_queues: List[Queue] = list()
        self.__command_serializer = command_serializer
        self.__command_deserializer = command_deserializer
        self.__command_registry = command_registry
        self.__producer: Optional[Producer] = None

    def _start(self) -> None:
        broker_channel = self.__broker_connection.channel()
        self.__create_dead_letter_exchange(broker_channel)
        for queue in self.__command_queues:
            queue.declare(channel=broker_channel)
        for process in self.__command_consumer_processes:
            process.start()
        self.__producer = Producer(broker_channel)

    def __create_dead_letter_exchange(self, channel: Channel) -> None:
        command_failure_exchange = Exchange(self.__DEAD_LETTER_EXCHANGE_NAME, type="fanout", channel=channel)
        command_failure_exchange.declare()

    @is_not_running
    def register(self, handler: CommandHandler) -> None:
        handler_command = self._get_handler_command(handler)
        if handler_command in self.__command_registry:
            raise HandlerForCommandAlreadyRegistered(handler_command.__name__)

        self.__command_registry.register(handler_command, handler.__class__.__name__)

        try:
            consumer, consumer_process = self.__create_consumer(handler, handler_command)
            self.__command_consumers.append(consumer)
            self.__command_consumer_processes.append(consumer_process)
        except Exception as ex:
            self.__command_registry.unregister(handler_command)
            raise ex

    def __create_consumer(
        self, command_handler: CommandHandler, command_cls: Type[Command]
    ) -> Tuple[PassengerKombuConsumer, Process]:
        handler_queue = Queue(
            command_cls.__name__, queue_arguments={"x-dead-letter-exchange": self.__DEAD_LETTER_EXCHANGE_NAME}
        )
        self.__command_queues.append(handler_queue)
        handler_consumer = PassengerKombuConsumer(
            self.__broker_connection,
            handler_queue,
            command_handler,
            command_cls,
            self._middleware_executor,
            self.__command_deserializer,
        )
        handler_process = Process(target=handler_consumer.run)
        return handler_consumer, handler_process

    @is_running
    def execute(self, command: Command) -> None:
        if command.__class__ not in self.__command_registry:
            raise HandlerNotFoundForCommand(command.__class__.__name__)
        self.__publish_command(command)

    def __publish_command(self, command: Command) -> None:
        serialized_command = self.__command_serializer.serialize(command)
        if self.__producer is not None:
            self.__producer.publish(
                serialized_command,
                exchange="",
                routing_key=command.__class__.__name__,
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
