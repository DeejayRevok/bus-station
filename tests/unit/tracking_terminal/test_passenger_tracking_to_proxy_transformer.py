from typing import Type
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.tracking_terminal.passenger_tracking_to_proxy_transformer import PassengerTrackingToProxyTransformer


class TestPassengerTrackingToProxyTransformer(TestCase):
    def setUp(self) -> None:
        self.passenger_tracking_to_proxy_transformer = PassengerTrackingToProxyTransformer()

    @patch("bus_station.tracking_terminal.passenger_tracking_to_proxy_transformer.asdict")
    def test_transform(self, asdict_mock):
        test_proxy_instance = Mock()
        test_proxy_class = Mock(spec=Type)
        test_proxy_class.return_value = test_proxy_instance
        test_instance_data = {"test": "test"}
        asdict_mock.return_value = test_instance_data
        test_instance = Mock()

        proxy_instance = self.passenger_tracking_to_proxy_transformer.transform(test_instance, test_proxy_class)

        self.assertEqual(test_proxy_instance, proxy_instance)
        asdict_mock.assert_called_once_with(test_instance)
        test_proxy_class.assert_called_once_with(**test_instance_data)
