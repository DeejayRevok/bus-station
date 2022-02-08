from dataclasses import asdict, dataclass

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from bus_station.query_terminal.middleware.implementations.tracking_query_middleware import TrackingQueryMiddleware
from bus_station.query_terminal.middleware.query_middleware_executor import QueryMiddlewareExecutor
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.tracking_terminal.mappers.sqlalchemy.sqlalchemy_query_tracking_mapper import (
    SQLAlchemyQueryTrackingMapper,
)
from bus_station.tracking_terminal.passenger_tracking_to_proxy_transformer import PassengerTrackingToProxyTransformer
from bus_station.tracking_terminal.proxy_to_passenger_tracking_transformer import ProxyToPassengerTrackingTransformer
from bus_station.tracking_terminal.repositories.implementations.sqlalchemy.sqlalchemy_query_tracking_repository import (
    SQLAlchemyQueryTrackingRepository,
)
from bus_station.tracking_terminal.trackers.sqlalchemy_passenger_tracker import SQLAlchemyPassengerTracker
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class QueryTest(Query):
    test: str


class QueryTestHandler(QueryHandler):
    def __init__(self, response_value: str):
        self.call_count = 0
        self.response_value = response_value

    def handle(self, query: QueryTest) -> QueryResponse:
        self.call_count = self.call_count + 1
        return QueryResponse(data=self.response_value)


class TestSQLAlchemyTrackingQueryMiddleware(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_env_ready = False
        cls.postgres_user = cls.postgres["user"]
        cls.postgres_password = cls.postgres["password"]
        cls.postgres_host = cls.postgres["host"]
        cls.postgres_port = cls.postgres["port"]
        cls.postgres_db = cls.postgres["db"]
        cls.sqlalchemy_engine = create_engine(
            f"postgresql://{cls.postgres_user}:{cls.postgres_password}"
            f"@{cls.postgres_host}:{cls.postgres_port}/{cls.postgres_db}"
        )
        cls.test_env_ready = True
        cls.sqlalchemy_metadata = MetaData(bind=cls.sqlalchemy_engine)
        clear_mappers()
        cls.sqlalchemy_query_tracking_mapper = SQLAlchemyQueryTrackingMapper(cls.sqlalchemy_metadata)
        cls.sqlalchemy_query_tracking_mapper.map()
        cls.sqlalchemy_metadata.create_all()
        cls.sqlalchemy_session = sessionmaker(bind=cls.sqlalchemy_engine)()
        cls.passenger_tracking_transformer = PassengerTrackingToProxyTransformer()
        cls.proxy_transformer = ProxyToPassengerTrackingTransformer()
        cls.sqlalchemy_query_tracking_repository = SQLAlchemyQueryTrackingRepository(
            cls.sqlalchemy_session, cls.passenger_tracking_transformer, cls.proxy_transformer
        )
        cls.sqlalchemy_query_tracker = SQLAlchemyPassengerTracker(
            cls.sqlalchemy_query_tracking_repository, cls.sqlalchemy_query_tracking_mapper
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.sqlalchemy_session.close()
        cls.sqlalchemy_metadata.drop_all()

    def setUp(self) -> None:
        if self.test_env_ready is False:
            self.fail("Test environment is not ready")
        self.query_middleware_executor = QueryMiddlewareExecutor()
        self.query_middleware_executor.add_middleware_definition(
            TrackingQueryMiddleware, self.sqlalchemy_query_tracker, lazy=False
        )

    def test_execute_with_middleware_tracks(self):
        test_query = QueryTest(test="test")
        test_query_handler = QueryTestHandler(response_value="test_response")

        self.query_middleware_executor.execute(test_query, test_query_handler)

        stored_tracking = self.sqlalchemy_query_tracking_repository.find_by_id(str(id(test_query)))
        self.assertIsNotNone(stored_tracking)
        self.assertEqual(test_query.__class__.__name__, stored_tracking.name)
        self.assertEqual(test_query_handler.__class__.__name__, stored_tracking.executor_name)
        self.assertEqual(asdict(test_query), stored_tracking.data)
        self.assertIsNotNone(stored_tracking.execution_start)
        self.assertIsNotNone(stored_tracking.execution_end)
        self.assertGreater(stored_tracking.execution_end, stored_tracking.execution_start)
        self.assertEqual(asdict(QueryResponse(data="test_response")), stored_tracking.response_data)
        self.assertEqual(1, test_query_handler.call_count)
