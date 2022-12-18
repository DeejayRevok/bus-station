from datetime import datetime

from pymongo import MongoClient

from bus_station.tracking_terminal.models.query_tracking import QueryTracking
from bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_deserializer import (
    MongoPassengerTrackingDeserializer,
)
from bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_serializer import (
    MongoPassengerTrackingSerializer,
)
from bus_station.tracking_terminal.repositories.implementations.pymongo.pymongo_query_tracking_repository import (
    PyMongoQueryTrackingRepository,
)
from tests.integration.integration_test_case import IntegrationTestCase


class TestPyMongoQueryTrackingRepository(IntegrationTestCase):
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
        cls.pymongo_db.drop_collection("query_tracking")
        cls.pymongo_client.close()

    def setUp(self) -> None:
        self.pymongo_query_tracking_repository = PyMongoQueryTrackingRepository(
            self.pymongo_db, self.mongo_tracking_serializer, self.mongo_tracking_deserializer
        )

    def test_save(self):
        query_tracking = QueryTracking(
            id="test_id",
            data={"test": "test"},
            name="test_query_tracking",
            executor_name="test_query_executor",
            execution_start=datetime.now(),
            execution_end=datetime.now(),
            success=True,
        )

        self.pymongo_query_tracking_repository.save(query_tracking)

        queried_serializer_query_tracking = self.pymongo_db.get_collection("query_tracking").find_one(
            filter={"_id": query_tracking.id}
        )
        self.assertIsNotNone(queried_serializer_query_tracking)
        queried_query_tracking = self.mongo_tracking_deserializer.deserialize(
            queried_serializer_query_tracking, QueryTracking
        )
        self.assertEqual(queried_query_tracking, query_tracking)

    def test_find_by_id(self):
        test_id = "test_id2"
        query_tracking_serialized = dict(
            _id=test_id,
            data={"test": "test"},
            name="test_query_tracking",
            executor_name="test_query_executor",
            execution_start=datetime.now().timestamp(),
            execution_end=datetime.now().timestamp(),
            success=False,
        )
        self.pymongo_db.get_collection("query_tracking").insert_one(query_tracking_serialized)

        found_query_tracking = self.pymongo_query_tracking_repository.find_by_id(test_id)

        expected_query_tracking = self.mongo_tracking_deserializer.deserialize(query_tracking_serialized, QueryTracking)
        self.assertEqual(expected_query_tracking, found_query_tracking)
