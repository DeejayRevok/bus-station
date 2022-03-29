from typing import Any, Optional, Set, Type

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.command_registry import CommandRegistry
from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.passengers.passenger_record.passenger_record import PassengerRecord
from bus_station.shared_terminal.bus_stop_resolver.bus_stop_resolver import BusStopResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter


class InMemoryCommandRegistry(CommandRegistry):
    def __init__(
        self,
        in_memory_repository: InMemoryPassengerRecordRepository,
        fqn_getter: FQNGetter,
        command_handler_resolver: BusStopResolver[CommandHandler],
        passenger_class_resolver: PassengerClassResolver,
    ):
        self.__in_memory_repository = in_memory_repository
        self.__fqn_getter = fqn_getter
        self.__command_handler_resolver = command_handler_resolver
        self.__passenger_class_resolver = passenger_class_resolver

    def _register(self, command: Type[Command], handler: CommandHandler, handler_contact: Any) -> None:
        self.__in_memory_repository.save(
            PassengerRecord(
                passenger_name=command.__name__,
                passenger_fqn=self.__fqn_getter.get(command),
                destination_fqn=self.__fqn_getter.get(handler),
                destination_contact=handler_contact,
            )
        )

    def get_command_destination(self, command: Type[Command]) -> Optional[CommandHandler]:
        command_records = self.__in_memory_repository.find_by_passenger_name(command.__name__)
        if command_records is None:
            return None

        command_handler_fqn = command_records[0].destination_fqn
        return self.__command_handler_resolver.resolve_from_fqn(command_handler_fqn)

    def get_command_destination_contact(self, command: Type[Command]) -> Optional[Any]:
        command_records = self.__in_memory_repository.find_by_passenger_name(command.__name__)
        if command_records is None:
            return None

        return command_records[0].destination_contact

    def get_commands_registered(self) -> Set[Type[Command]]:
        commands_registered = set()
        for command_record in self.__in_memory_repository.all():
            command = self.__passenger_class_resolver.resolve_from_fqn(command_record.passenger_fqn)
            if command is None or not issubclass(command, Command):
                continue
            commands_registered.add(command)
        return commands_registered

    def unregister(self, command: Type[Command]) -> None:
        self.__in_memory_repository.delete_by_passenger_name(command.__name__)
