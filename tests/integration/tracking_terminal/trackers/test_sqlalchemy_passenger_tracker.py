from dataclasses import asdict, dataclass

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.tracking_terminal.mappers.sqlalchemy.sqlalchemy_event_tracking_mapper import (
    SQLAlchemyEventTrackingMapper,
)
from bus_station.tracking_terminal.models.proxy_definitions import SAEventTrackingProxy
from bus_station.tracking_terminal.passenger_tracking_to_proxy_transformer import PassengerTrackingToProxyTransformer
from bus_station.tracking_terminal.proxy_to_passenger_tracking_transformer import ProxyToPassengerTrackingTransformer
from bus_station.tracking_terminal.repositories.implementations.sqlalchemy.sqlalchemy_event_tracking_repository import (
    SQLAlchemyEventTrackingRepository,
)
from bus_station.tracking_terminal.trackers.passenger_tracking_not_found import PassengerTrackingNotFound
from bus_station.tracking_terminal.trackers.sqlalchemy_passenger_tracker import SQLAlchemyPassengerTracker
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class EventTest(Event):
    test: str


class EventTestConsumer(EventConsumer):
    def consume(self, event: EventTest) -> None:
        pass


class TestSQLAlchemyPassengerTracker(IntegrationTestCase):
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
        cls.sqlalchemy_event_tracking_mapper = SQLAlchemyEventTrackingMapper(cls.sqlalchemy_metadata)
        cls.sqlalchemy_event_tracking_mapper.map()
        cls.sqlalchemy_metadata.create_all()
        cls.sqlalchemy_session = sessionmaker(bind=cls.sqlalchemy_engine)()
        cls.passenger_tracking_transformer = PassengerTrackingToProxyTransformer()
        cls.proxy_transformer = ProxyToPassengerTrackingTransformer()
        cls.sqlalchemy_event_tracking_repository = SQLAlchemyEventTrackingRepository(
            cls.sqlalchemy_session, cls.passenger_tracking_transformer, cls.proxy_transformer
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.sqlalchemy_session.close()
        cls.sqlalchemy_metadata.drop_all()

    def setUp(self) -> None:
        self.sqlalchemy_passenger_tracker = SQLAlchemyPassengerTracker(
            self.sqlalchemy_event_tracking_repository, self.sqlalchemy_event_tracking_mapper
        )

    def tearDown(self) -> None:
        self.sqlalchemy_session.query(SAEventTrackingProxy).delete()

    def test_start_tracking(self):
        test_event = EventTest(test="test")
        test_event_consumer = EventTestConsumer()

        self.sqlalchemy_passenger_tracker.start_tracking(test_event, test_event_consumer)

        stored_tracking = self.sqlalchemy_event_tracking_repository.find_by_id(str(id(test_event)))
        self.assertIsNotNone(stored_tracking)
        self.assertEqual(test_event.__class__.__name__, stored_tracking.name)
        self.assertEqual(test_event_consumer.__class__.__name__, stored_tracking.executor_name)
        self.assertEqual(asdict(test_event), stored_tracking.data)
        self.assertIsNotNone(stored_tracking.execution_start)
        self.assertIsNone(stored_tracking.execution_end)

    def test_end_tracking(self):
        test_event = EventTest(test="test")
        test_event_consumer = EventTestConsumer()
        self.sqlalchemy_passenger_tracker.start_tracking(test_event, test_event_consumer)

        self.sqlalchemy_passenger_tracker.end_tracking(test_event)

        stored_tracking = self.sqlalchemy_event_tracking_repository.find_by_id(str(id(test_event)))
        self.assertIsNotNone(stored_tracking)
        self.assertEqual(test_event.__class__.__name__, stored_tracking.name)
        self.assertEqual(test_event_consumer.__class__.__name__, stored_tracking.executor_name)
        self.assertEqual(asdict(test_event), stored_tracking.data)
        self.assertIsNotNone(stored_tracking.execution_start)
        self.assertIsNotNone(stored_tracking.execution_end)
        self.assertGreater(stored_tracking.execution_end, stored_tracking.execution_start)

    def test_end_tracking_error(self):
        test_event = EventTest(test="test")

        with self.assertRaises(PassengerTrackingNotFound) as ptnf:
            self.sqlalchemy_passenger_tracker.end_tracking(test_event)

        self.assertEqual(test_event.__class__.__name__, ptnf.exception.passenger_name)
        self.assertEqual(str(id(test_event)), ptnf.exception.passenger_tracking_id)
