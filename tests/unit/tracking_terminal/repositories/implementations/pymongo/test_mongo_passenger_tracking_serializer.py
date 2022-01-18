from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, Mock, call

from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking
from bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_serializer import (
    MongoPassengerTrackingSerializer,
)


class TestMongoPassengerTrackingSerializer(TestCase):
    def setUp(self) -> None:
        self.serializer = MongoPassengerTrackingSerializer()

    @patch(
        "bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_serializer."
        "asdict"
    )
    def test_serialize(self, asdict_mock):
        test_datetime = Mock(spec=datetime)
        test_tracking_instance = Mock(spec=PassengerTracking)
        test_tracking_instance.execution_start = test_datetime
        test_tracking_instance.execution_end = test_datetime
        test_datetime_timestamp = 123421
        test_datetime.timestamp.return_value = test_datetime_timestamp
        test_id = "test_id"
        test_serialized_data = {"id": test_id}
        asdict_mock.return_value = test_serialized_data

        serialized_tracking = self.serializer.serialize(test_tracking_instance)

        expected_serialized_tracking = test_serialized_data
        expected_serialized_tracking["_id"] = test_id
        expected_serialized_tracking["execution_start"] = test_datetime_timestamp
        expected_serialized_tracking["execution_end"] = test_datetime_timestamp
        self.assertEqual(expected_serialized_tracking, serialized_tracking)
        test_datetime.timestamp.assert_has_calls([call(), call()])
        asdict_mock.assert_called_once_with(test_tracking_instance)
