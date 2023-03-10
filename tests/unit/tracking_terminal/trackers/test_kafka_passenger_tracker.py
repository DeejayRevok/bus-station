from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

from confluent_kafka.cimpl import Producer
from freezegun import freeze_time

from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.bus_stop import BusStop
from bus_station.shared_terminal.kafka_topic_creator import KafkaTopicCreator
from bus_station.tracking_terminal.models.passenger_model_tracking_map import PassengerModelTrackingMap
from bus_station.tracking_terminal.models.passenger_tracking_serializer import PassengerTrackingSerializer
from bus_station.tracking_terminal.trackers.kafka_passenger_tracker import KafkaPassengerTracker


class PassengerMock(Passenger):
    @classmethod
    def passenger_name(cls) -> str:
        return "test"


class TestKafkaPassengerTracker(TestCase):
    def setUp(self) -> None:
        self.kafka_producer_mock = Mock(spec=Producer)
        self.kafka_topic_creator_mock = Mock(spec=KafkaTopicCreator)
        self.passenger_tracking_serializer_mock = Mock(spec=PassengerTrackingSerializer)
        self.passenger_tracking_model_map_mock = Mock(spec=PassengerModelTrackingMap)
        self.kafka_passenger_tracker = KafkaPassengerTracker(
            self.kafka_producer_mock,
            self.kafka_topic_creator_mock,
            self.passenger_tracking_serializer_mock,
            self.passenger_tracking_model_map_mock
        )

    @freeze_time()
    @patch("bus_station.tracking_terminal.trackers.passenger_tracker.asdict")
    def test_start_tracking(self, asdict_mock):
        tracking_model_mock = MagicMock()
        self.passenger_tracking_model_map_mock.get_tracking_model.return_value = tracking_model_mock
        passenger_mock = PassengerMock()
        bus_stop_mock = Mock(spec=BusStop)
        self.passenger_tracking_serializer_mock.serialize.return_value = "test_serialized_passenger_tracking"

        self.kafka_passenger_tracker.start_tracking(passenger_mock, bus_stop_mock)

        self.passenger_tracking_model_map_mock.get_tracking_model.assert_called_once_with(passenger_mock)
        tracking_model_mock.assert_called_once_with(
            passenger_id=passenger_mock.passenger_id,
            name=passenger_mock.passenger_name(),
            executor_name=bus_stop_mock.bus_stop_name(),
            data=asdict_mock(passenger_mock),
            execution_start=datetime.now(),
            execution_end=None,
            success=None,
        )
        self.kafka_topic_creator_mock.create.assert_called_once_with(tracking_model_mock.__class__.__name__)
        self.kafka_producer_mock.produce.assert_called_once_with(
            topic=tracking_model_mock.__class__.__name__,
            value="test_serialized_passenger_tracking"
        )
        self.kafka_producer_mock.poll.assert_called_once_with(0)

    @freeze_time()
    @patch("bus_station.tracking_terminal.trackers.passenger_tracker.asdict")
    def test_end_tracking(self, asdict_mock):
        tracking_model_mock = MagicMock()
        self.passenger_tracking_model_map_mock.get_tracking_model.return_value = tracking_model_mock
        passenger_mock = PassengerMock()
        bus_stop_mock = Mock(spec=BusStop)
        self.passenger_tracking_serializer_mock.serialize.return_value = "test_serialized_passenger_tracking"

        self.kafka_passenger_tracker.end_tracking(passenger_mock, bus_stop_mock, True)

        self.passenger_tracking_model_map_mock.get_tracking_model.assert_called_once_with(passenger_mock)
        tracking_model_mock.assert_called_once_with(
            passenger_id=passenger_mock.passenger_id,
            name=passenger_mock.passenger_name(),
            executor_name=bus_stop_mock.bus_stop_name(),
            data=asdict_mock(passenger_mock),
            execution_start=None,
            execution_end=datetime.now(),
            success=True,
        )
        self.kafka_topic_creator_mock.create.assert_called_once_with(tracking_model_mock.__class__.__name__)
        self.kafka_producer_mock.produce.assert_called_once_with(
            topic=tracking_model_mock.__class__.__name__,
            value="test_serialized_passenger_tracking"
        )
        self.kafka_producer_mock.poll.assert_called_once_with(0)
