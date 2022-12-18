from datetime import datetime

from pymongo import MongoClient

from bus_station.tracking_terminal.models.command_tracking import CommandTracking
from bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_deserializer import (
    MongoPassengerTrackingDeserializer,
)
from bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_serializer import (
    MongoPassengerTrackingSerializer,
)
from bus_station.tracking_terminal.repositories.implementations.pymongo.pymongo_command_tracking_repository import (
    PyMongoCommandTrackingRepository,
)
from tests.integration.integration_test_case import IntegrationTestCase


class TestPyMongoCommandTrackingRepository(IntegrationTestCase):
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
        cls.pymongo_db.drop_collection("command_tracking")
        cls.pymongo_client.close()

    def setUp(self) -> None:
        self.pymongo_command_tracking_repository = PyMongoCommandTrackingRepository(
            self.pymongo_db, self.mongo_tracking_serializer, self.mongo_tracking_deserializer
        )

    def test_save(self):
        command_tracking = CommandTracking(
            id="test_id",
            data={"test": "test"},
            name="test_command_tracking",
            executor_name="test_command_executor",
            execution_start=datetime.now(),
            execution_end=datetime.now(),
            success=False,
        )

        self.pymongo_command_tracking_repository.save(command_tracking)

        queried_serializer_command_tracking = self.pymongo_db.get_collection("command_tracking").find_one(
            filter={"_id": command_tracking.id}
        )
        self.assertIsNotNone(queried_serializer_command_tracking)
        queried_command_tracking = self.mongo_tracking_deserializer.deserialize(
            queried_serializer_command_tracking, CommandTracking
        )
        self.assertEqual(queried_command_tracking, command_tracking)

    def test_find_by_id(self):
        test_id = "test_id2"
        command_tracking_serialized = dict(
            _id=test_id,
            data={"test": "test"},
            name="test_command_tracking",
            executor_name="test_command_executor",
            execution_start=datetime.now().timestamp(),
            execution_end=datetime.now().timestamp(),
            success=True,
        )
        self.pymongo_db.get_collection("command_tracking").insert_one(command_tracking_serialized)

        found_command_tracking = self.pymongo_command_tracking_repository.find_by_id(test_id)

        expected_command_tracking = self.mongo_tracking_deserializer.deserialize(
            command_tracking_serialized, CommandTracking
        )
        self.assertEqual(expected_command_tracking, found_command_tracking)
