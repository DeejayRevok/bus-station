from unittest import TestCase
from unittest.mock import Mock, patch

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient

from bus_station.shared_terminal.kafka_topic_creator import KafkaTopicCreator
from bus_station.tracking_terminal.builders.kafka_passenger_tracker_builder import KafkaPassengerTrackerBuilder
from bus_station.tracking_terminal.models.passenger_model_tracking_map import PassengerModelTrackingMap
from bus_station.tracking_terminal.models.passenger_tracking_json_serializer import PassengerTrackingJSONSerializer
from bus_station.tracking_terminal.trackers.kafka_passenger_tracker import KafkaPassengerTracker


class TestKafkaPassengerTrackerBuilder(TestCase):
    def setUp(self) -> None:
        self.bootstrap_servers = "test_bootstrap_servers"
        self.builder = KafkaPassengerTrackerBuilder(kafka_bootstrap_servers=self.bootstrap_servers)

    @patch("bus_station.tracking_terminal.builders.kafka_passenger_tracker_builder.KafkaPassengerTracker")
    @patch("bus_station.tracking_terminal.builders.kafka_passenger_tracker_builder.KafkaTopicCreator")
    @patch("bus_station.tracking_terminal.builders.kafka_passenger_tracker_builder.AdminClient")
    @patch("bus_station.tracking_terminal.builders.kafka_passenger_tracker_builder.Producer")
    def test_build(
        self,
        producer_builder_mock,
        admin_client_builder_mock,
        kafka_topic_creator_builder_mock,
        kafka_passenger_tracker_builder_mock,
    ):
        producer_mock = Mock(spec=Producer)
        producer_builder_mock.return_value = producer_mock
        admin_client_mock = Mock(spec=AdminClient)
        admin_client_builder_mock.return_value = admin_client_mock
        kafka_topic_creator_mock = Mock(spec=KafkaTopicCreator)
        kafka_topic_creator_builder_mock.return_value = kafka_topic_creator_mock
        kafka_passenger_tracker_mock = Mock(spec=KafkaPassengerTracker)
        kafka_passenger_tracker_builder_mock.return_value = kafka_passenger_tracker_mock
        passenger_tracking_json_serializer_mock = Mock(spec=PassengerTrackingJSONSerializer)
        passenger_model_tracking_map_mock = Mock(spec=PassengerModelTrackingMap)
        test_client_id = "test_client_id"

        tracker = (
            self.builder.with_passenger_tracking_serializer(passenger_tracking_json_serializer_mock)
            .with_passenger_model_tracking_map(passenger_model_tracking_map_mock)
            .build(test_client_id)
        )

        self.assertEqual(tracker, kafka_passenger_tracker_mock)
        producer_builder_mock.assert_called_once_with(
            {"bootstrap.servers": self.bootstrap_servers, "client.id": test_client_id, "queue.buffering.max.ms": 10}
        )
        admin_client_builder_mock.assert_called_once_with({"bootstrap.servers": self.bootstrap_servers})
        kafka_topic_creator_builder_mock.assert_called_once_with(admin_client_mock)
        kafka_passenger_tracker_builder_mock.assert_called_once_with(
            kafka_producer=producer_mock,
            kafka_topic_creator=kafka_topic_creator_mock,
            passenger_tracking_serializer=passenger_tracking_json_serializer_mock,
            passenger_model_tracking_map=passenger_model_tracking_map_mock,
        )
