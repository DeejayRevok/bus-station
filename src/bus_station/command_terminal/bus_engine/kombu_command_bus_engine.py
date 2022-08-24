from typing import ClassVar, Type, TypeVar

from kombu import Connection
from kombu.messaging import Exchange, Queue
from kombu.transport.virtual import Channel

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.contact_not_found_for_command import ContactNotFoundForCommand
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.engine.engine import Engine

C = TypeVar("C", bound=Command)


class KombuCommandBusEngine(Engine):
    __DEAD_LETTER_EXCHANGE_NAME: ClassVar = "failed_commands"

    def __init__(
        self,
        broker_connection: Connection,
        command_registry: RemoteCommandRegistry,
        command_receiver: PassengerReceiver[Command, CommandHandler],
        command_deserializer: PassengerDeserializer,
        command_type: Type[C],
    ):
        super().__init__()
        command_handler = command_registry.get_command_destination(command_type)
        if command_handler is None:
            raise HandlerNotFoundForCommand(command_type.__name__)

        broker_connection = broker_connection
        channel = broker_connection.channel()
        self.__create_dead_letter_exchange(channel)

        command_queue_name = command_registry.get_command_destination_contact(command_type)
        if command_queue_name is None:
            raise ContactNotFoundForCommand(command_type.__name__)

        command_queue = self.__create_command_handler_queue(command_queue_name, channel)

        self.__command_consumer = PassengerKombuConsumer(
            broker_connection,
            command_queue,
            command_handler,
            command_type,
            command_receiver,
            command_deserializer,
        )

    def start(self) -> None:
        try:
            self.__command_consumer.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        self.__command_consumer.stop()

    def __create_dead_letter_exchange(self, channel: Channel) -> None:
        command_failure_exchange = Exchange(self.__DEAD_LETTER_EXCHANGE_NAME, type="fanout", channel=channel)
        command_failure_exchange.declare()

    def __create_command_handler_queue(self, command_queue_name: str, channel: Channel) -> Queue:
        command_queue = Queue(
            name=command_queue_name, queue_arguments={"x-dead-letter-exchange": self.__DEAD_LETTER_EXCHANGE_NAME}
        )
        command_queue.declare(channel=channel)
        return command_queue
