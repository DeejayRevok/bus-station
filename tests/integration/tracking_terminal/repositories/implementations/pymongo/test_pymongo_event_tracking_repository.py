from datetime import datetime

from pymongo import MongoClient

from bus_station.tracking_terminal.models.event_tracking import EventTracking
from bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_deserializer import (
    MongoPassengerTrackingDeserializer,
)
from bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_serializer import (
    MongoPassengerTrackingSerializer,
)
from bus_station.tracking_terminal.repositories.implementations.pymongo.pymongo_event_tracking_repository import (
    PyMongoEventTrackingRepository,
)
from tests.integration.integration_test_case import IntegrationTestCase


class TestPyMongoEventTrackingRepository(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mongo_user = cls.mongo["user"]
        cls.mongo_password = cls.mongo["password"]
        cls.mongo_host = cls.mongo["host"]
        cls.mongo_port = cls.mongo["port"]
        cls.mongo_db = cls.mongo["db"]
        cls.pymongo_client = MongoClient(
            f"mongodb://{cls.mongo_user}:{cls.mongo_password}" f"@{cls.mongo_host}:{cls.mongo_port}"
        )
        cls.pymongo_db = cls.pymongo_client.get_database(cls.mongo_db)
        cls.mongo_tracking_serializer = MongoPassengerTrackingSerializer()
        cls.mongo_tracking_deserializer = MongoPassengerTrackingDeserializer()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.pymongo_db.drop_collection("event_tracking")
        cls.pymongo_client.close()

    def setUp(self) -> None:
        self.pymongo_event_tracking_repository = PyMongoEventTrackingRepository(
            self.pymongo_db, self.mongo_tracking_serializer, self.mongo_tracking_deserializer
        )

    def test_save(self):
        event_tracking = EventTracking(
            id="test_id",
            data={"test": "test"},
            name="test_event_tracking",
            executor_name="test_event_executor",
            execution_start=datetime.now(),
            execution_end=datetime.now(),
        )

        self.pymongo_event_tracking_repository.save(event_tracking)

        queried_serializer_event_tracking = self.pymongo_db.get_collection("event_tracking").find_one(
            filter={"_id": event_tracking.id}
        )
        self.assertIsNotNone(queried_serializer_event_tracking)
        queried_event_tracking = self.mongo_tracking_deserializer.deserialize(
            queried_serializer_event_tracking, EventTracking
        )
        self.assertEqual(queried_event_tracking, event_tracking)

    def test_find_by_id(self):
        test_id = "test_id2"
        event_tracking_serialized = dict(
            _id=test_id,
            data={"test": "test"},
            name="test_event_tracking",
            executor_name="test_event_executor",
            execution_start=datetime.now().timestamp(),
            execution_end=datetime.now().timestamp(),
        )
        self.pymongo_db.get_collection("event_tracking").insert_one(event_tracking_serialized)

        found_event_tracking = self.pymongo_event_tracking_repository.find_by_id(test_id)

        expected_event_tracking = self.mongo_tracking_deserializer.deserialize(event_tracking_serialized, EventTracking)
        self.assertEqual(expected_event_tracking, found_event_tracking)
