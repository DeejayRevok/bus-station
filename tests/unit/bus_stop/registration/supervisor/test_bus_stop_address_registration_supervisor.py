from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.bus_stop.registration.supervisor.bus_stop_address_registration_supervisor import (
    BusStopAddressRegistrationSupervisor,
)


class TestBusStopAddressRegistrationSupervisor(TestCase):
    def setUp(self) -> None:
        self.bus_stop_address_registry_mock = Mock(spec=BusStopAddressRegistry)
        self.bus_stop_address_registration_supervisor = BusStopAddressRegistrationSupervisor(
            self.bus_stop_address_registry_mock
        )

    @patch(
        "bus_station.bus_stop.registration.supervisor.bus_stop_address_registration_supervisor"
        ".get_bus_stop_address_from_environment"
    )
    def test_on_register(self, get_bus_stop_address_from_environment_mock) -> None:
        get_bus_stop_address_from_environment_mock.return_value = "bus_stop_address"

        self.bus_stop_address_registration_supervisor.on_register("bus_stop_id")

        self.bus_stop_address_registry_mock.register.assert_called_once_with("bus_stop_id", "bus_stop_address")

    def test_on_unregister(self) -> None:
        self.bus_stop_address_registration_supervisor.on_unregister("bus_stop_id")

        self.bus_stop_address_registry_mock.unregister.assert_called_once_with("bus_stop_id")
