from unittest import TestCase
from unittest.mock import Mock

from redis.client import Redis

from bus_station.bus_stop.registration.address.redis_bus_stop_address_registry import RedisBusStopAddressRegistry


class TestRedisBusStopAddressRegistry(TestCase):
    def setUp(self):
        self.redis_client = Mock(spec=Redis)
        self.registry = RedisBusStopAddressRegistry(self.redis_client)

    def test_register(self):
        self.registry.register("bus_stop_id", "address")

        self.redis_client.set.assert_called_once_with("bus_stop_id", "address")

    def test_get_bus_stop_address(self):
        self.redis_client.get.return_value = b"address"

        address = self.registry.get_bus_stop_address("bus_stop_id")

        self.redis_client.get.assert_called_once_with("bus_stop_id")
        self.assertEqual("address", address)

    def test_unregister(self):
        self.registry.unregister("bus_stop_id")

        self.redis_client.delete.assert_called_once_with("bus_stop_id")
