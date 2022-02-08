from dataclasses import asdict, dataclass

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.middleware.command_middleware_executor import CommandMiddlewareExecutor
from bus_station.command_terminal.middleware.implementations.tracking_command_middleware import (
    TrackingCommandMiddleware,
)
from bus_station.tracking_terminal.mappers.sqlalchemy.sqlalchemy_command_tracking_mapper import (
    SQLAlchemyCommandTrackingMapper,
)
from bus_station.tracking_terminal.passenger_tracking_to_proxy_transformer import PassengerTrackingToProxyTransformer
from bus_station.tracking_terminal.proxy_to_passenger_tracking_transformer import ProxyToPassengerTrackingTransformer
from bus_station.tracking_terminal.repositories.implementations.sqlalchemy import sqlalchemy_command_tracking_repository
from bus_station.tracking_terminal.trackers.sqlalchemy_passenger_tracker import SQLAlchemyPassengerTracker
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    test: str


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = 0

    def handle(self, command: CommandTest) -> None:
        self.call_count = self.call_count + 1


class TestSQLAlchemyTrackingCommandMiddleware(IntegrationTestCase):
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
        cls.sqlalchemy_command_tracking_mapper = SQLAlchemyCommandTrackingMapper(cls.sqlalchemy_metadata)
        cls.sqlalchemy_command_tracking_mapper.map()
        cls.sqlalchemy_metadata.create_all()
        cls.sqlalchemy_session = sessionmaker(bind=cls.sqlalchemy_engine)()
        cls.passenger_tracking_transformer = PassengerTrackingToProxyTransformer()
        cls.proxy_transformer = ProxyToPassengerTrackingTransformer()
        cls.sqlalchemy_command_tracking_repository = (
            sqlalchemy_command_tracking_repository.SQLAlchemyCommandTrackingRepository(
                cls.sqlalchemy_session, cls.passenger_tracking_transformer, cls.proxy_transformer
            )
        )
        cls.sqlalchemy_command_tracker = SQLAlchemyPassengerTracker(
            cls.sqlalchemy_command_tracking_repository, cls.sqlalchemy_command_tracking_mapper
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.sqlalchemy_session.close()
        cls.sqlalchemy_metadata.drop_all()

    def setUp(self) -> None:
        if self.test_env_ready is False:
            self.fail("Test environment is not ready")
        self.command_middleware_executor = CommandMiddlewareExecutor()
        self.command_middleware_executor.add_middleware_definition(
            TrackingCommandMiddleware, self.sqlalchemy_command_tracker, lazy=False
        )

    def test_execute_with_middleware_tracks(self):
        test_command = CommandTest(test="test")
        test_command_handler = CommandTestHandler()

        self.command_middleware_executor.execute(test_command, test_command_handler)

        stored_tracking = self.sqlalchemy_command_tracking_repository.find_by_id(str(id(test_command)))
        self.assertIsNotNone(stored_tracking)
        self.assertEqual(test_command.__class__.__name__, stored_tracking.name)
        self.assertEqual(test_command_handler.__class__.__name__, stored_tracking.executor_name)
        self.assertEqual(asdict(test_command), stored_tracking.data)
        self.assertIsNotNone(stored_tracking.execution_start)
        self.assertIsNotNone(stored_tracking.execution_end)
        self.assertGreater(stored_tracking.execution_end, stored_tracking.execution_start)
        self.assertEqual(1, test_command_handler.call_count)
