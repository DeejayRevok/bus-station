from typing import Callable
from unittest import TestCase
from unittest.mock import Mock, patch

from rpyc import Connection

from bus_station.bus_stop.registration.address.address_not_found_for_passenger import AddressNotFoundForPassenger
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus import RPyCCommandBus
from bus_station.command_terminal.command import Command
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class TestRPyCCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_serializer_mock = Mock(spec=PassengerSerializer)
        self.address_registry_mock = Mock(spec=BusStopAddressRegistry)
        self.rpyc_command_bus = RPyCCommandBus(
            self.command_serializer_mock,
            self.address_registry_mock,
        )

    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    def test_transport_passenger_address_not_found(self, get_context_root_passenger_id_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.return_value = None

        with self.assertRaises(AddressNotFoundForPassenger) as anffp:
            self.rpyc_command_bus.transport(test_command)

        self.assertEqual("test_command", anffp.exception.passenger_name)
        self.command_serializer_mock.serialize.assert_not_called()
        test_command.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.assert_called_once_with(
            test_command.__class__
        )

    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus.connect")
    def test_transport_success(self, connect_mock, get_context_root_passenger_id_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        test_host = "test_host"
        test_port = "41124"
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.return_value = f"{test_host}:{test_port}"
        test_rpyc_connection = Mock(spec=Connection)
        connect_mock.return_value = test_rpyc_connection
        test_serialized_command = "test_serialized_command"
        self.command_serializer_mock.serialize.return_value = test_serialized_command
        test_rpyc_callable = Mock(spec=Callable)
        setattr(test_rpyc_connection.root, test_command.passenger_name(), test_rpyc_callable)

        self.rpyc_command_bus.transport(test_command)

        connect_mock.assert_called_once_with(test_host, port=test_port, config={"allow_public_attrs": True})
        self.command_serializer_mock.serialize.assert_called_once_with(test_command)
        test_rpyc_callable.assert_called_once_with(test_serialized_command)
        test_rpyc_connection.close.assert_called_once_with()
        test_command.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")
        self.address_registry_mock.get_address_for_bus_stop_passenger_class.assert_called_once_with(
            test_command.__class__
        )
