from datetime import datetime
from typing import Type
from unittest import TestCase
from unittest.mock import Mock, call, patch

from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking
from bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_deserializer import (
    MongoPassengerTrackingDeserializer,
)


class TestMongoPassengerTrackingDeserializer(TestCase):
    def setUp(self) -> None:
        self.deserializer = MongoPassengerTrackingDeserializer()

    @patch(
        "bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_deserializer."
        "datetime"
    )
    def test_deserialize_success(self, datetime_mock):
        test_datetime = Mock(spec=datetime)
        datetime_mock.fromtimestamp.return_value = test_datetime
        test_tracking_cls = Mock(spec=Type[PassengerTracking])
        test_tracking = Mock(spec=PassengerTracking)
        test_tracking_cls.return_value = test_tracking
        test_start_timestamp = 3412123
        test_end_timestamp = 234324
        test_id = "test_id"
        test_serialized_tracking_data = {
            "_id": test_id,
            "execution_start": test_start_timestamp,
            "execution_end": test_end_timestamp,
        }

        deserialized_item = self.deserializer.deserialize(test_serialized_tracking_data, test_tracking_cls)

        self.assertEqual(test_tracking, deserialized_item)
        datetime_mock.fromtimestamp.assert_has_calls([call(test_start_timestamp), call(test_end_timestamp)])
        test_tracking_cls.assert_called_once_with(
            id=test_id, execution_start=test_datetime, execution_end=test_datetime
        )
