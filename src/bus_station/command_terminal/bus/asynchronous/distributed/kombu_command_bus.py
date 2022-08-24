from kombu import Connection
from kombu.messaging import Producer

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class KombuCommandBus(CommandBus):
    def __init__(
        self,
        broker_connection: Connection,
        command_serializer: PassengerSerializer,
        command_registry: RemoteCommandRegistry,
    ):
        self.__broker_connection = broker_connection
        self.__command_serializer = command_serializer
        self.__command_registry = command_registry
        self.__producer = Producer(broker_connection.channel())

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

    def shutdown(self) -> None:
        self.__producer.release()
