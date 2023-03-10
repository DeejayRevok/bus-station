from concurrent.futures import Future
from unittest import TestCase
from unittest.mock import Mock, patch

from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic, KafkaException, KafkaError

from bus_station.shared_terminal.kafka_topic_creator import KafkaTopicCreator


class TestKafkaTopicCreator(TestCase):
    def setUp(self) -> None:
        self.kafka_admin_client_mock = Mock(spec=AdminClient)
        self.kafka_topic_creator = KafkaTopicCreator(
            self.kafka_admin_client_mock
        )

    @patch("bus_station.shared_terminal.kafka_topic_creator.NewTopic")
    def test_create_repeated_calls(self, new_topic_mock):
        creation_future_mock = Mock(spec=Future)
        self.kafka_admin_client_mock.create_topics.return_value = {"new_topic": creation_future_mock}
        test_new_topic = Mock(spec=NewTopic)
        new_topic_mock.return_value = test_new_topic

        self.kafka_topic_creator.create("new_topic")
        self.kafka_topic_creator.create("new_topic")

        new_topic_mock.assert_called_once_with("new_topic", 4)
        self.kafka_admin_client_mock.create_topics.assert_called_once_with([test_new_topic])
        creation_future_mock.result.assert_called_once_with()

    @patch("bus_station.shared_terminal.kafka_topic_creator.NewTopic")
    def test_create_already_existing_topic(self, new_topic_mock):
        test_kafka_error = KafkaError(error=KafkaError.TOPIC_ALREADY_EXISTS)
        test_exception = KafkaException(test_kafka_error)
        creation_future_mock = Mock(spec=Future)
        self.kafka_admin_client_mock.create_topics.return_value = {"new_topic": creation_future_mock}
        test_new_topic = Mock(spec=NewTopic)
        new_topic_mock.return_value = test_new_topic
        creation_future_mock.result.side_effect = test_exception

        self.kafka_topic_creator.create("new_topic")

        new_topic_mock.assert_called_once_with("new_topic", 4)
        self.kafka_admin_client_mock.create_topics.assert_called_once_with([test_new_topic])
        creation_future_mock.result.assert_called_once_with()

    @patch("bus_station.shared_terminal.kafka_topic_creator.NewTopic")
    def test_create_error(self, new_topic_mock):
        test_kafka_error = KafkaError(error=KafkaError.KAFKA_STORAGE_ERROR)
        test_exception = KafkaException(test_kafka_error)
        creation_future_mock = Mock(spec=Future)
        self.kafka_admin_client_mock.create_topics.return_value = {"new_topic": creation_future_mock}
        test_new_topic = Mock(spec=NewTopic)
        new_topic_mock.return_value = test_new_topic
        creation_future_mock.result.side_effect = test_exception

        with self.assertRaises(KafkaException) as context:
            self.kafka_topic_creator.create("new_topic")

        self.assertEqual(test_exception, context.exception)
        new_topic_mock.assert_called_once_with("new_topic", 4)
        self.kafka_admin_client_mock.create_topics.assert_called_once_with([test_new_topic])
        creation_future_mock.result.assert_called_once_with()
