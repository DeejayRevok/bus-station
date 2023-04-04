from typing import Any, Optional, Set, Type

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.command_registry import CommandRegistry
from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.passengers.passenger_record.passenger_record import PassengerRecord
from bus_station.passengers.passenger_resolvers import resolve_passenger_class_from_fqn
from bus_station.shared_terminal.bus_stop_resolver.bus_stop_resolver import BusStopResolver
from bus_station.shared_terminal.fqn import resolve_fqn


class InMemoryCommandRegistry(CommandRegistry):
    def __init__(
        self,
        in_memory_repository: InMemoryPassengerRecordRepository,
        command_handler_resolver: BusStopResolver[CommandHandler],
    ):
        self.__in_memory_repository = in_memory_repository
        self.__command_handler_resolver = command_handler_resolver

    def _register(self, command: Type[Command], handler: CommandHandler, handler_contact: Any) -> None:
        self.__in_memory_repository.save(
            PassengerRecord(
                passenger_name=command.passenger_name(),
                passenger_fqn=resolve_fqn(command),
                destination_name=handler.bus_stop_name(),
                destination_fqn=resolve_fqn(handler),
                destination_contact=handler_contact,
            )
        )

    def get_command_destination(self, command_name: str) -> Optional[CommandHandler]:
        command_records = self.__in_memory_repository.find_by_passenger_name(command_name)
        if command_records is None:
            return None

        command_handler_fqn = command_records[0].destination_fqn
        return self.__command_handler_resolver.resolve_from_fqn(command_handler_fqn)

    def get_command_destination_contact(self, command_name: str) -> Optional[Any]:
        command_records = self.__in_memory_repository.find_by_passenger_name(command_name)
        if command_records is None:
            return None

        return command_records[0].destination_contact

    def get_commands_registered(self) -> Set[Type[Command]]:
        commands_registered = set()
        for command_record in self.__in_memory_repository.all():
            command = resolve_passenger_class_from_fqn(command_record.passenger_fqn)
            if command is None or not issubclass(command, Command):
                continue
            commands_registered.add(command)
        return commands_registered

    def unregister(self, command_name: str) -> None:
        self.__in_memory_repository.delete_by_passenger_name(command_name)
