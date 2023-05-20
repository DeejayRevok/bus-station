from dataclasses import dataclass
from json import loads
from threading import Thread
from time import sleep

from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.shared_terminal.kafka_topic_creator import KafkaTopicCreator
from bus_station.tracking_terminal.models.passenger_model_tracking_map import PassengerModelTrackingMap
from bus_station.tracking_terminal.models.passenger_tracking_json_serializer import PassengerTrackingJSONSerializer
from bus_station.tracking_terminal.trackers.kafka_passenger_tracker import KafkaPassengerTracker
from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.tracking_terminal.trackers.kafka_test_consumer import KafkaTestConsumer


@dataclass(frozen=True)
class TestCommand(Command):
    test: str


class TestCommandHandler(CommandHandler):
    def handle(self, command: TestCommand) -> None:
        pass


class TestKafkaPassengerTracker(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        bootstrap_servers = f"{cls.kafka['host']}:{cls.kafka['port']}"
        cls.kafka_producer = Producer(
            {"bootstrap.servers": bootstrap_servers, "client.id": "bus-station-test", "queue.buffering.max.ms": 10}
        )
        kafka_admin_client = AdminClient({"bootstrap.servers": bootstrap_servers})
        kafka_topic_creator = KafkaTopicCreator(kafka_admin_client)
        passenger_tracking_model_map = PassengerModelTrackingMap()
        passenger_tracking_serializer = PassengerTrackingJSONSerializer()
        cls.kafka_tracker = KafkaPassengerTracker(
            cls.kafka_producer, kafka_topic_creator, passenger_tracking_serializer, passenger_tracking_model_map
        )
        kafka_consumer = Consumer(
            {"bootstrap.servers": bootstrap_servers, "auto.offset.reset": "smallest", "group.id": "test_consumer"}
        )
        topic_name = "CommandTracking"
        kafka_topic_creator.create(topic_name)
        kafka_consumer.subscribe([topic_name])
        cls.kafka_test_consumer = KafkaTestConsumer(kafka_consumer)
        cls.consumer_thread = Thread(target=cls.kafka_test_consumer.consume)
        cls.consumer_thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.kafka_test_consumer.running = False
        sleep(2)

    def setUp(self) -> None:
        self.kafka_test_consumer.received_message_data = None

    def test_start_tracking(self):
        test_command = TestCommand(test="test_data")
        test_command.set_root_passenger_id("test_root_passenger_id")
        test_command_handler = TestCommandHandler()

        self.kafka_tracker.start_tracking(passenger=test_command, bus_stop=test_command_handler)

        self.kafka_producer.flush()
        sleep(5)
        self.assertIsNotNone(self.kafka_test_consumer.received_message_data)
        received_message_dict = loads(self.kafka_test_consumer.received_message_data)
        self.assertEqual(test_command.passenger_id, received_message_dict["passenger_id"])
        self.assertEqual(test_command.root_passenger_id, received_message_dict["root_passenger_id"])
        self.assertEqual(test_command.passenger_name(), received_message_dict["name"])
        self.assertEqual(test_command_handler.bus_stop_name(), received_message_dict["executor_name"])
        self.assertEqual(
            {
                "test": "test_data",
            },
            received_message_dict["data"],
        )
        self.assertIsNotNone(received_message_dict["execution_start"])
        self.assertIsNone(received_message_dict["execution_end"])
        self.assertIsNone(received_message_dict["success"])

    def test_end_tracking(self):
        test_command = TestCommand(test="test_data")
        test_command_handler = TestCommandHandler()
        test_command.set_root_passenger_id("test_root_passenger_id")

        self.kafka_tracker.end_tracking(passenger=test_command, bus_stop=test_command_handler, success=True)

        self.kafka_producer.flush()
        sleep(5)
        self.assertIsNotNone(self.kafka_test_consumer.received_message_data)
        received_message_dict = loads(self.kafka_test_consumer.received_message_data)
        self.assertEqual(test_command.passenger_id, received_message_dict["passenger_id"])
        self.assertEqual(test_command.root_passenger_id, received_message_dict["root_passenger_id"])
        self.assertEqual(test_command.passenger_name(), received_message_dict["name"])
        self.assertEqual(test_command_handler.bus_stop_name(), received_message_dict["executor_name"])
        self.assertEqual(
            {
                "test": "test_data",
            },
            received_message_dict["data"],
        )
        self.assertIsNone(received_message_dict["execution_start"])
        self.assertIsNotNone(received_message_dict["execution_end"])
        self.assertTrue(received_message_dict["success"])
