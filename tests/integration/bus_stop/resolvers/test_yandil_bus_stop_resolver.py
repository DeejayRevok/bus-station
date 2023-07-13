from unittest import TestCase

from yandil.configuration.configuration_container import default_configuration_container
from yandil.container import Container

from bus_station.bus_stop.resolvers.yandil_bus_stop_resolver import YandilBusStopResolver
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.shared_terminal.fqn import resolve_fqn


class BusStopTest(EventConsumer):
    @classmethod
    def bus_stop_name(cls) -> str:
        return "test_bus_stop"

    def consume(self, event: Event) -> None:
        pass


class TestClass:
    pass


class TestYandilBusStopResolver(TestCase):
    def setUp(self) -> None:
        self.container = Container(configuration_container=default_configuration_container)
        self.resolver = YandilBusStopResolver(container=self.container)

    def test_resolve(self):
        test_bus_stop = BusStopTest()
        self.container[BusStopTest] = test_bus_stop
        test_bus_stop_fqn = resolve_fqn(test_bus_stop)

        resolved_bus_stop = self.resolver.resolve(test_bus_stop_fqn)

        self.assertEqual(test_bus_stop, resolved_bus_stop)

    def test_resolve_invalid_instance(self):
        self.container[TestClass] = TestClass()
        test_bus_stop_fqn = resolve_fqn(TestClass)

        with self.assertRaises(TypeError):
            self.resolver.resolve(test_bus_stop_fqn)
