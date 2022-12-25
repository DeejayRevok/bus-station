from dataclasses import asdict, dataclass

from pymongo import MongoClient

from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_deserializer import (
    MongoPassengerTrackingDeserializer,
)
from bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_serializer import (
    MongoPassengerTrackingSerializer,
)
from bus_station.tracking_terminal.repositories.implementations.pymongo.pymongo_query_tracking_repository import (
    PyMongoQueryTrackingRepository,
)
from bus_station.tracking_terminal.trackers.passenger_tracking_not_found import PassengerTrackingNotFound
from bus_station.tracking_terminal.trackers.pymongo_passenger_tracker import PyMongoPassengerTracker
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class QueryTest(Query):
    test: str


class QueryTestHandler(QueryHandler):
    def handle(self, query: QueryTest) -> QueryResponse:
        return QueryResponse(data=query.test)


class TestPyMongoPassengerTracker(IntegrationTestCase):
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
        cls.pymongo_query_tracking_repository = PyMongoQueryTrackingRepository(
            cls.pymongo_db, cls.mongo_tracking_serializer, cls.mongo_tracking_deserializer
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.pymongo_client.drop_database(cls.mongo_db)
        cls.pymongo_client.close()

    def setUp(self) -> None:
        self.pymongo_passenger_tracker = PyMongoPassengerTracker(self.pymongo_query_tracking_repository)

    def tearDown(self) -> None:
        self.pymongo_db.drop_collection("query_tracking")

    def test_start_tracking(self):
        test_query = QueryTest(test="test")
        test_query_handler = QueryTestHandler()

        self.pymongo_passenger_tracker.start_tracking(test_query, test_query_handler)

        stored_tracking = self.pymongo_query_tracking_repository.find_by_id(str(id(test_query)))
        self.assertIsNotNone(stored_tracking)
        self.assertEqual(test_query.passenger_name(), stored_tracking.name)
        self.assertEqual(test_query_handler.bus_stop_name(), stored_tracking.executor_name)
        self.assertEqual(asdict(test_query), stored_tracking.data)
        self.assertIsNotNone(stored_tracking.execution_start)
        self.assertIsNone(stored_tracking.execution_end)

    def test_end_tracking(self):
        test_query = QueryTest(test="test")
        test_query_handler = QueryTestHandler()
        test_response = asdict(QueryResponse(data=test_query.test))
        self.pymongo_passenger_tracker.start_tracking(test_query, test_query_handler)

        self.pymongo_passenger_tracker.end_tracking(test_query, success=True, response_data=test_response)

        stored_tracking = self.pymongo_query_tracking_repository.find_by_id(str(id(test_query)))
        self.assertIsNotNone(stored_tracking)
        self.assertEqual(test_query.passenger_name(), stored_tracking.name)
        self.assertEqual(test_query_handler.bus_stop_name(), stored_tracking.executor_name)
        self.assertEqual(asdict(test_query), stored_tracking.data)
        self.assertEqual(test_response, stored_tracking.response_data)
        self.assertIsNotNone(stored_tracking.execution_start)
        self.assertIsNotNone(stored_tracking.execution_end)
        self.assertGreater(stored_tracking.execution_end, stored_tracking.execution_start)
        self.assertTrue(stored_tracking.success)

    def test_end_tracking_error(self):
        test_query = QueryTest(test="test")

        with self.assertRaises(PassengerTrackingNotFound) as ptnf:
            self.pymongo_passenger_tracker.end_tracking(test_query, success=False)

        self.assertEqual(test_query.passenger_name(), ptnf.exception.passenger_name)
        self.assertEqual(str(id(test_query)), ptnf.exception.passenger_tracking_id)
