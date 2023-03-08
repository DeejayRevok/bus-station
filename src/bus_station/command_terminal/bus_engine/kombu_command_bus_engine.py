from typing import ClassVar

from kombu import Connection, Exchange, Queue
from kombu.transport.base import StdChannel

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.contact_not_found_for_command import ContactNotFoundForCommand
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.resolve_passenger_from_bus_stop import resolve_passenger_from_bus_stop
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.engine.engine import Engine


class KombuCommandBusEngine(Engine):
    __DEAD_LETTER_EXCHANGE_NAME: ClassVar = "failed_commands"

    def __init__(
        self,
        broker_connection: Connection,
        command_registry: RemoteCommandRegistry,
        command_receiver: PassengerReceiver[Command, CommandHandler],
        command_deserializer: PassengerDeserializer,
        command_name: str,
    ):
        super().__init__()
        command_handler = command_registry.get_command_destination(command_name)
        if command_handler is None:
            raise HandlerNotFoundForCommand(command_name)

        broker_connection = broker_connection
        channel = broker_connection.channel()
        self.__create_dead_letter_exchange(channel)

        command_queue_name = command_registry.get_command_destination_contact(command_name)
        if command_queue_name is None:
            raise ContactNotFoundForCommand(command_name)

        command_queue = self.__create_command_handler_queue(command_queue_name, channel)

        command_type = resolve_passenger_from_bus_stop(command_handler, "handle", "command", Command)

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
        command_failure_exchange.declare()  # pyre-ignore[16]

    def __create_command_handler_queue(self, command_queue_name: str, channel: StdChannel) -> Queue:
        command_queue = Queue(
            name=command_queue_name, queue_arguments={"x-dead-letter-exchange": self.__DEAD_LETTER_EXCHANGE_NAME}
        )
        command_queue.declare(channel=channel)  # pyre-ignore[16]
        return command_queue
