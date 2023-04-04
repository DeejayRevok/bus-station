from dataclasses import dataclass

from redis import Redis

from bus_station.event_terminal.consumer_for_event_already_registered import ConsumerForEventAlreadyRegistered
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.redis_event_registry import RedisEventRegistry
from bus_station.passengers.passenger_record.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class EventTest(Event):
    pass


class EventTestConsumer(EventConsumer):
    def consume(self, event: EventTest) -> None:
        pass


class TestRedisEventRegistry(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)

    def setUp(self) -> None:
        self.redis_repository = RedisPassengerRecordRepository(self.redis_client)
        self.event_consumer_resolver = InMemoryBusStopResolver()
        self.redis_registry = RedisEventRegistry(
            redis_repository=self.redis_repository,
            event_consumer_resolver=self.event_consumer_resolver,
        )

    def tearDown(self) -> None:
        self.redis_registry.unregister(EventTest.passenger_name())

    def test_register(self):
        test_event_handler = EventTestConsumer()
        test_destination_contact = "test_destination_contact"
        self.event_consumer_resolver.add_bus_stop(test_event_handler)

        self.redis_registry.register(test_event_handler, test_destination_contact)

        self.assertCountEqual(
            [test_event_handler], self.redis_registry.get_event_destinations(EventTest.passenger_name())
        )
        self.assertCountEqual(
            [test_destination_contact], self.redis_registry.get_event_destination_contacts(EventTest.passenger_name())
        )

    def test_register_duplicate(self):
        test_event_handler = EventTestConsumer()
        test_destination_contact = "test_destination_contact"
        self.event_consumer_resolver.add_bus_stop(test_event_handler)

        self.redis_registry.register(test_event_handler, test_destination_contact)
        self.redis_registry.register(test_event_handler, test_destination_contact)

        self.assertCountEqual(
            [test_event_handler], self.redis_registry.get_event_destinations(EventTest.passenger_name())
        )
        self.assertEqual(
            {test_destination_contact}, self.redis_registry.get_event_destination_contacts(EventTest.passenger_name())
        )

    def test_register_consumer_for_event_already_registered(self):
        test_event_handler = EventTestConsumer()
        test_destination_contact = "test_destination_contact"
        self.event_consumer_resolver.add_bus_stop(test_event_handler)

        self.redis_registry.register(test_event_handler, test_destination_contact)
        with self.assertRaises(ConsumerForEventAlreadyRegistered) as context:
            self.redis_registry.register(test_event_handler, test_destination_contact + "different")

        self.assertEqual(EventTestConsumer.bus_stop_name(), context.exception.consumer_name)
        self.assertEqual(EventTest.passenger_name(), context.exception.event_name)
        self.assertCountEqual(
            [test_event_handler], self.redis_registry.get_event_destinations(EventTest.passenger_name())
        )
        self.assertEqual(
            {test_destination_contact}, self.redis_registry.get_event_destination_contacts(EventTest.passenger_name())
        )

    def test_unregister(self):
        test_event_handler = EventTestConsumer()
        test_destination_contact = "test_destination_contact"
        self.redis_registry.register(test_event_handler, test_destination_contact)
        self.event_consumer_resolver.add_bus_stop(test_event_handler)

        self.redis_registry.unregister(EventTest.passenger_name())

        self.assertIsNone(self.redis_registry.get_event_destinations(EventTest.passenger_name()))

    def test_get_events_registered(self):
        test_event_handler = EventTestConsumer()
        test_destination_contact = "test_destination_contact"
        self.redis_registry.register(test_event_handler, test_destination_contact)
        self.event_consumer_resolver.add_bus_stop(test_event_handler)

        registered_passengers = self.redis_registry.get_events_registered()

        expected_events_registered = {EventTest}
        self.assertCountEqual(expected_events_registered, registered_passengers)
