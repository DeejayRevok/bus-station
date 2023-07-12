from typing import ClassVar

from kombu import Connection, Exchange, Queue
from kombu.transport.base import StdChannel

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_not_found import CommandHandlerNotFound
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.engine.engine import Engine


class KombuCommandBusEngine(Engine):
    __DEAD_LETTER_EXCHANGE_NAME: ClassVar = "failed_commands"

    def __init__(
        self,
        broker_connection: Connection,
        command_handler_registry: CommandHandlerRegistry,
        command_receiver: PassengerReceiver[Command, CommandHandler],
        command_deserializer: PassengerDeserializer,
        command_handler_name: str,
    ):
        command_handler = command_handler_registry.get_bus_stop_by_name(command_handler_name)
        if command_handler is None:
            raise CommandHandlerNotFound(command_handler_name)

        command_type = command_handler.passenger()
        channel = broker_connection.channel()
        self.__create_dead_letter_exchange(channel)

        command_queue = self.__create_command_handler_queue(command_type.passenger_name(), channel)

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

    def __create_dead_letter_exchange(self, channel: StdChannel) -> None:
        command_failure_exchange = Exchange(self.__DEAD_LETTER_EXCHANGE_NAME, type="fanout", channel=channel)
        command_failure_exchange.declare()

    def __create_command_handler_queue(self, command_queue_name: str, channel: StdChannel) -> Queue:
        command_queue = Queue(
            name=command_queue_name, queue_arguments={"x-dead-letter-exchange": self.__DEAD_LETTER_EXCHANGE_NAME}
        )
        command_queue.declare(channel=channel)
        return command_queue
