from dataclasses import dataclass, asdict
from unittest import TestCase

import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, clear_mappers

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware_executor import EventMiddlewareExecutor
from bus_station.event_terminal.middleware.implementations.tracking_event_middleware import (
    TrackingEventMiddleware,
)
from bus_station.tracking_terminal.mappers.sqlalchemy.sqlalchemy_event_tracking_mapper import (
    SQLAlchemyEventTrackingMapper,
)
from bus_station.tracking_terminal.passenger_tracking_to_proxy_transformer import PassengerTrackingToProxyTransformer
from bus_station.tracking_terminal.proxy_to_passenger_tracking_transformer import ProxyToPassengerTrackingTransformer
from bus_station.tracking_terminal.repositories.implementations.sqlalchemy.sqlalchemy_event_tracking_repository import (
    SQLAlchemyEventTrackingRepository,
)
from bus_station.tracking_terminal.trackers.sqlalchemy_passenger_tracker import SQLAlchemyPassengerTracker


@dataclass(frozen=True)
class EventTest(Event):
    test: str


class EventTestConsumer(EventConsumer):
    def __init__(self):
        self.call_count = 0

    def consume(self, event: EventTest) -> None:
        self.call_count = self.call_count + 1


@pytest.mark.usefixtures("postgres")
class TestSQLAlchemyTrackingEventMiddleware(TestCase):
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
        cls.sqlalchemy_event_tracking_mapper = SQLAlchemyEventTrackingMapper(cls.sqlalchemy_metadata)
        cls.sqlalchemy_event_tracking_mapper.map()
        cls.sqlalchemy_metadata.create_all()
        cls.sqlalchemy_session = sessionmaker(bind=cls.sqlalchemy_engine)()
        cls.passenger_tracking_transformer = PassengerTrackingToProxyTransformer()
        cls.proxy_transformer = ProxyToPassengerTrackingTransformer()
        cls.sqlalchemy_event_tracking_repository = SQLAlchemyEventTrackingRepository(
            cls.sqlalchemy_session, cls.passenger_tracking_transformer, cls.proxy_transformer
        )
        cls.sqlalchemy_event_tracker = SQLAlchemyPassengerTracker(
            cls.sqlalchemy_event_tracking_repository, cls.sqlalchemy_event_tracking_mapper
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.sqlalchemy_session.close()
        cls.sqlalchemy_metadata.drop_all()

    def setUp(self) -> None:
        if self.test_env_ready is False:
            self.fail("Test environment is not ready")
        self.event_middleware_executor = EventMiddlewareExecutor()
        self.event_middleware_executor.add_middleware_definition(
            TrackingEventMiddleware, self.sqlalchemy_event_tracker, lazy=False
        )

    def test_execute_with_middleware_tracks(self):
        test_event = EventTest(test="test")
        test_event_handler = EventTestConsumer()

        self.event_middleware_executor.execute(test_event, test_event_handler)

        stored_tracking = self.sqlalchemy_event_tracking_repository.find_by_id(str(id(test_event)))
        self.assertIsNotNone(stored_tracking)
        self.assertEqual(test_event.__class__.__name__, stored_tracking.name)
        self.assertEqual(test_event_handler.__class__.__name__, stored_tracking.executor_name)
        self.assertEqual(asdict(test_event), stored_tracking.data)
        self.assertIsNotNone(stored_tracking.execution_start)
        self.assertIsNotNone(stored_tracking.execution_end)
        self.assertGreater(stored_tracking.execution_end, stored_tracking.execution_start)
        self.assertEqual(1, test_event_handler.call_count)
