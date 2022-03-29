from datetime import datetime

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, clear_mappers, sessionmaker

from bus_station.tracking_terminal.mappers.sqlalchemy.sqlalchemy_command_tracking_mapper import (
    SQLAlchemyCommandTrackingMapper,
)
from bus_station.tracking_terminal.models.command_tracking import CommandTracking
from bus_station.tracking_terminal.models.proxy_definitions import SACommandTrackingProxy
from bus_station.tracking_terminal.passenger_tracking_to_proxy_transformer import PassengerTrackingToProxyTransformer
from bus_station.tracking_terminal.proxy_to_passenger_tracking_transformer import ProxyToPassengerTrackingTransformer
from bus_station.tracking_terminal.repositories.implementations.sqlalchemy import sqlalchemy_command_tracking_repository
from tests.integration.integration_test_case import IntegrationTestCase


class TestSQLAlchemyCommandTrackingRepository(IntegrationTestCase):
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
        cls.sqlalchemy_command_tracking_mapper = SQLAlchemyCommandTrackingMapper(cls.sqlalchemy_metadata)
        cls.sqlalchemy_command_tracking_mapper.map()
        cls.sqlalchemy_metadata.create_all()
        cls.sqlalchemy_session_maker = sessionmaker(bind=cls.sqlalchemy_engine)
        cls.passenger_tracking_transformer = PassengerTrackingToProxyTransformer()
        cls.proxy_transformer = ProxyToPassengerTrackingTransformer()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.sqlalchemy_metadata.drop_all()

    def setUp(self) -> None:
        self.sqlalchemy_session: Session = self.sqlalchemy_session_maker()
        self.sqlalchemy_command_tracking_repository = (
            sqlalchemy_command_tracking_repository.SQLAlchemyCommandTrackingRepository(
                sqlalchemy_session=self.sqlalchemy_session,
                passenger_tracking_transformer=self.passenger_tracking_transformer,
                proxy_transformer=self.proxy_transformer,
            )
        )

    def tearDown(self) -> None:
        self.sqlalchemy_session.close()

    def test_save(self):
        command_tracking = CommandTracking(
            id="test_id",
            data={"test": "test"},
            name="test_command_tracking",
            executor_name="test_command_executor",
            execution_start=datetime.now(),
            execution_end=datetime.now(),
        )

        self.sqlalchemy_command_tracking_repository.save(command_tracking)

        queried_command_tracking_proxy = (
            self.sqlalchemy_session.query(SACommandTrackingProxy).filter_by(id=command_tracking.id).one_or_none()
        )
        self.assertIsNotNone(queried_command_tracking_proxy)
        queried_command_tracking = self.proxy_transformer.transform(queried_command_tracking_proxy, CommandTracking)
        self.assertEqual(queried_command_tracking, command_tracking)

    def test_find_by_id(self):
        proxy_command_tracking = SACommandTrackingProxy(
            id="test_id",
            data={"test": "test"},
            name="test_command_tracking",
            executor_name="test_command_executor",
            execution_start=datetime.now(),
            execution_end=datetime.now(),
        )
        self.sqlalchemy_session.add(proxy_command_tracking)
        self.sqlalchemy_session.commit()

        found_command_tracking = self.sqlalchemy_command_tracking_repository.find_by_id(proxy_command_tracking.id)

        expected_command_tracking = self.proxy_transformer.transform(proxy_command_tracking, CommandTracking)
        self.assertEqual(expected_command_tracking, found_command_tracking)
