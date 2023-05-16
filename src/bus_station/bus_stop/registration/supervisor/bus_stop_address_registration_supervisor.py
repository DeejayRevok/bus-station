from typing import Optional

from bus_station.bus_stop.environment import get_bus_stop_address_from_environment
from bus_station.bus_stop.registration.address.address_not_found_for_bus_stop import AddressNotFoundForBusStop
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.bus_stop.registration.supervisor.bus_stop_registration_supervisor import BusStopRegistrationSupervisor


class BusStopAddressRegistrationSupervisor(BusStopRegistrationSupervisor):
    def __init__(self, address_registry: BusStopAddressRegistry):
        self.__address_registry = address_registry

    def on_register(self, bus_stop_id: str) -> None:
        bus_stop_address = self.__get_bus_stop_address(bus_stop_id)
        if bus_stop_address is None:
            raise AddressNotFoundForBusStop(bus_stop_id)
        self.__address_registry.register(bus_stop_id, bus_stop_address)

    def __get_bus_stop_address(self, bus_stop_id: str) -> Optional[str]:
        return get_bus_stop_address_from_environment(bus_stop_id)

    def on_unregister(self, bus_stop_id: str) -> None:
        self.__address_registry.unregister(bus_stop_id)
