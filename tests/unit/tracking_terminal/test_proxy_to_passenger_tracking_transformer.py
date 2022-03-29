from typing import Type
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.tracking_terminal.proxy_to_passenger_tracking_transformer import ProxyToPassengerTrackingTransformer


class TestProxyToPassengerTrackingTransformer(TestCase):
    def setUp(self) -> None:
        self.proxy_to_passenger_tracking_transformer = ProxyToPassengerTrackingTransformer()

    @patch("bus_station.tracking_terminal.proxy_to_passenger_tracking_transformer.asdict")
    def test_transform(self, asdict_mock):
        test_instance = Mock()
        test_instance_class = Mock(spec=Type)
        test_instance_class.return_value = test_instance
        test_proxy_data = {"test": "test"}
        asdict_mock.return_value = test_proxy_data
        test_proxy = Mock()

        instance = self.proxy_to_passenger_tracking_transformer.transform(test_proxy, test_instance_class)

        self.assertEqual(test_instance, instance)
        asdict_mock.assert_called_once_with(test_proxy)
        test_instance_class.assert_called_once_with(**test_proxy_data)
