from datetime import datetime

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, clear_mappers, sessionmaker

from bus_station.tracking_terminal.mappers.sqlalchemy.sqlalchemy_query_tracking_mapper import (
    SQLAlchemyQueryTrackingMapper,
)
from bus_station.tracking_terminal.models.proxy_definitions import SAQueryTrackingProxy
from bus_station.tracking_terminal.models.query_tracking import QueryTracking
from bus_station.tracking_terminal.passenger_tracking_to_proxy_transformer import PassengerTrackingToProxyTransformer
from bus_station.tracking_terminal.proxy_to_passenger_tracking_transformer import ProxyToPassengerTrackingTransformer
from bus_station.tracking_terminal.repositories.implementations.sqlalchemy.sqlalchemy_query_tracking_repository import (
    SQLAlchemyQueryTrackingRepository,
)
from tests.integration.integration_test_case import IntegrationTestCase


class TestSQLAlchemyEventTrackingRepository(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.postgres_user = cls.postgres["user"]
        cls.postgres_password = cls.postgres["password"]
        cls.postgres_host = cls.postgres["host"]
        cls.postgres_port = cls.postgres["port"]
        cls.postgres_db = cls.postgres["db"]
        cls.sqlalchemy_engine = create_engine(
            f"postgresql://{cls.postgres_user}:{cls.postgres_password}"
            f"@{cls.postgres_host}:{cls.postgres_port}/{cls.postgres_db}"
        )
        cls.sqlalchemy_metadata = MetaData(bind=cls.sqlalchemy_engine)
        clear_mappers()
        cls.sqlalchemy_query_tracking_mapper = SQLAlchemyQueryTrackingMapper(cls.sqlalchemy_metadata)
        cls.sqlalchemy_query_tracking_mapper.map()
        cls.sqlalchemy_metadata.create_all()
        cls.sqlalchemy_session_maker = sessionmaker(bind=cls.sqlalchemy_engine)
        cls.passenger_tracking_transformer = PassengerTrackingToProxyTransformer()
        cls.proxy_transformer = ProxyToPassengerTrackingTransformer()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.sqlalchemy_metadata.drop_all()

    def setUp(self) -> None:
        self.sqlalchemy_session: Session = self.sqlalchemy_session_maker()
        self.sqlalchemy_query_tracking_repository = SQLAlchemyQueryTrackingRepository(
            sqlalchemy_session=self.sqlalchemy_session,
            passenger_tracking_transformer=self.passenger_tracking_transformer,
            proxy_transformer=self.proxy_transformer,
        )

    def tearDown(self) -> None:
        self.sqlalchemy_session.close()

    def test_save(self):
        query_tracking = QueryTracking(
            id="test_id",
            data={"test": "test"},
            name="test_command_tracking",
            executor_name="test_command_executor",
            execution_start=datetime.now(),
            execution_end=datetime.now(),
            response_data={"test_response": "test_response"},
        )

        self.sqlalchemy_query_tracking_repository.save(query_tracking)

        queried_query_tracking_proxy = (
            self.sqlalchemy_session.query(SAQueryTrackingProxy).filter_by(id=query_tracking.id).one_or_none()
        )
        queried_query_tracking = self.proxy_transformer.transform(queried_query_tracking_proxy, QueryTracking)
        self.assertEqual(queried_query_tracking, query_tracking)

    def test_find_by_id(self):
        query_tracking_proxy = SAQueryTrackingProxy(
            id="test_id",
            data={"test": "test"},
            name="test_command_tracking",
            executor_name="test_command_executor",
            execution_start=datetime.now(),
            execution_end=datetime.now(),
            response_data={"test_response": "test_response"},
        )
        self.sqlalchemy_session.add(query_tracking_proxy)
        self.sqlalchemy_session.commit()

        found_query_tracking = self.sqlalchemy_query_tracking_repository.find_by_id(query_tracking_proxy.id)

        expected_query_tracking = self.proxy_transformer.transform(query_tracking_proxy, QueryTracking)
        self.assertEqual(expected_query_tracking, found_query_tracking)
