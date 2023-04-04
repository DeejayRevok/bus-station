from unittest import TestCase

from bus_station.command_terminal.bus.synchronous.sync_command_bus import SyncCommandBus
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.shared_terminal.fqn import resolve_fqn


class TestFqn(TestCase):
    def test_resolve_fqn_from_instance(self):
        serializer = PassengerJSONSerializer()
        fqn = resolve_fqn(serializer)

        expected_fqn = "bus_station.passengers.serialization.passenger_json_serializer.PassengerJSONSerializer"
        self.assertEqual(expected_fqn, fqn)

    def test_resolve_fqn_from_class(self):
        fqn = resolve_fqn(SyncCommandBus)

        expected_fqn = "bus_station.command_terminal.bus.synchronous.sync_command_bus.SyncCommandBus"
        self.assertEqual(expected_fqn, fqn)
