from dataclasses import dataclass

from bus_station.event_terminal.consumer_for_event_already_registered import ConsumerForEventAlreadyRegistered
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry
from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class EventTest(Event):
    pass


class EventTestConsumer(EventConsumer):
    def consume(self, event: EventTest) -> None:
        pass


class TestInMemoryEventRegistry(IntegrationTestCase):
    def setUp(self) -> None:
        self.in_memory_repository = InMemoryPassengerRecordRepository()
        self.fqn_getter = FQNGetter()
        self.event_consumer_resolver = InMemoryBusStopResolver(fqn_getter=self.fqn_getter)
        self.passenger_class_resolver = PassengerClassResolver()
        self.in_memory_registry = InMemoryEventRegistry(
            in_memory_repository=self.in_memory_repository,
            event_consumer_resolver=self.event_consumer_resolver,
            fqn_getter=self.fqn_getter,
            passenger_class_resolver=self.passenger_class_resolver,
        )

    def tearDown(self) -> None:
        self.in_memory_registry.unregister(EventTest.passenger_name())

    def test_register(self):
        test_event_handler = EventTestConsumer()
        test_destination_contact = "test_destination_contact"
        self.event_consumer_resolver.add_bus_stop(test_event_handler)

        self.in_memory_registry.register(test_event_handler, test_destination_contact)

        self.assertCountEqual(
            [test_event_handler], self.in_memory_registry.get_event_destinations(EventTest.passenger_name())
        )
        self.assertEqual(
            {test_destination_contact},
            self.in_memory_registry.get_event_destination_contacts(EventTest.passenger_name()),
        )

    def test_register_duplicate(self):
        test_event_handler = EventTestConsumer()
        test_destination_contact = "test_destination_contact"
        self.event_consumer_resolver.add_bus_stop(test_event_handler)

        self.in_memory_registry.register(test_event_handler, test_destination_contact)
        self.in_memory_registry.register(test_event_handler, test_destination_contact)

        self.assertCountEqual(
            [test_event_handler], self.in_memory_registry.get_event_destinations(EventTest.passenger_name())
        )
        self.assertEqual(
            {test_destination_contact},
            self.in_memory_registry.get_event_destination_contacts(EventTest.passenger_name()),
        )

    def test_register_consumer_for_event_already_registered(self):
        test_event_handler = EventTestConsumer()
        test_destination_contact = "test_destination_contact"
        self.event_consumer_resolver.add_bus_stop(test_event_handler)

        self.in_memory_registry.register(test_event_handler, test_destination_contact)
        with self.assertRaises(ConsumerForEventAlreadyRegistered) as context:
            self.in_memory_registry.register(test_event_handler, test_destination_contact + "different")

        self.assertEqual(EventTestConsumer.bus_stop_name(), context.exception.consumer_name)
        self.assertEqual(EventTest.passenger_name(), context.exception.event_name)
        self.assertCountEqual(
            [test_event_handler], self.in_memory_registry.get_event_destinations(EventTest.passenger_name())
        )
        self.assertEqual(
            {test_destination_contact},
            self.in_memory_registry.get_event_destination_contacts(EventTest.passenger_name()),
        )

    def test_unregister(self):
        test_event_handler = EventTestConsumer()
        test_destination_contact = "test_destination_contact"
        self.in_memory_registry.register(test_event_handler, test_destination_contact)
        self.event_consumer_resolver.add_bus_stop(test_event_handler)

        self.in_memory_registry.unregister(EventTest.passenger_name())

        self.assertIsNone(self.in_memory_registry.get_event_destinations(EventTest.passenger_name()))

    def test_get_events_registered(self):
        test_event_handler = EventTestConsumer()
        test_destination_contact = "test_destination_contact"
        self.in_memory_registry.register(test_event_handler, test_destination_contact)
        self.event_consumer_resolver.add_bus_stop(test_event_handler)

        registered_passengers = self.in_memory_registry.get_events_registered()

        expected_events_registered = {EventTest}
        self.assertCountEqual(expected_events_registered, registered_passengers)
