from typing import List, Optional, Set, Type

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.passenger_record import PassengerRecord
from bus_station.passengers.passenger_record.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.shared_terminal.bus_stop_resolver.bus_stop_resolver import BusStopResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter


class RedisCommandRegistry(RemoteCommandRegistry):
    def __init__(
        self,
        redis_repository: RedisPassengerRecordRepository,
        fqn_getter: FQNGetter,
        command_handler_resolver: BusStopResolver[CommandHandler],
        passenger_class_resolver: PassengerClassResolver,
    ):
        self.__redis_repository = redis_repository
        self.__fqn_getter = fqn_getter
        self.__command_handler_resolver = command_handler_resolver
        self.__passenger_class_resolver = passenger_class_resolver

    def _register(self, command: Type[Command], handler: CommandHandler, handler_contact: str) -> None:
        self.__redis_repository.save(
            PassengerRecord(
                passenger_name=command.passenger_name(),
                passenger_fqn=self.__fqn_getter.get(command),
                destination_name=handler.bus_stop_name(),
                destination_fqn=self.__fqn_getter.get(handler),
                destination_contact=handler_contact,
            )
        )

    def get_command_destination_contact(self, command_name: str) -> Optional[str]:
        command_records = self.__redis_repository.find_by_passenger_name(command_name)
        if command_records is None:
            return None

        return command_records[0].destination_contact

    def get_commands_registered(self) -> Set[Type[Command]]:
        commands_registered = set()
        for command_record in self.__redis_repository.all():
            command = self.__passenger_class_resolver.resolve_from_fqn(command_record.passenger_fqn)
            if command is None or not issubclass(command, Command):
                continue
            commands_registered.add(command)
        return commands_registered

    def get_command_destination(self, command_name: str) -> Optional[CommandHandler]:
        command_records: Optional[List[PassengerRecord[str]]] = self.__redis_repository.find_by_passenger_name(
            command_name
        )
        if command_records is None:
            return None

        command_handler_fqn = command_records[0].destination_fqn
        return self.__command_handler_resolver.resolve_from_fqn(command_handler_fqn)

    def unregister(self, command_name: str) -> None:
        self.__redis_repository.delete_by_passenger_name(command_name)
