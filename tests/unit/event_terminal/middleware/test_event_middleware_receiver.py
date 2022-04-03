from typing import Type
from unittest import TestCase
from unittest.mock import Mock, call

from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware import EventMiddleware
from bus_station.event_terminal.middleware.event_middleware_receiver import EventMiddlewareReceiver


class TestEventMiddlewareReceiver(TestCase):
    def setUp(self) -> None:
        self.event_middleware_receiver = EventMiddlewareReceiver()

    def test_add_middleware_definition_lazy(self):
        test_middleware_class = Mock(spec=EventMiddleware.__class__)
        test_arg = "test_arg"

        self.event_middleware_receiver.add_middleware_definition(test_middleware_class, test_arg, lazy=True)

        test_middleware_class.assert_not_called()

    def test_add_middleware_definition_not_lazy(self):
        test_middleware_class = Mock(spec=EventMiddleware.__class__)
        test_arg = "test_arg"

        self.event_middleware_receiver.add_middleware_definition(test_middleware_class, test_arg, lazy=False)

        test_middleware_class.assert_called_once_with(test_arg)

    def test_receiver_success(self):
        parent_mock = Mock()
        test_middleware1_class = Mock(spec=Type[EventMiddleware])
        test_middleware2_class = Mock(spec=Type[EventMiddleware])
        test_event = Mock(spec=Event)
        test_event_consumer = Mock(spec=EventConsumer)
        parent_mock.middleware1_class = test_middleware1_class
        parent_mock.middleware2_class = test_middleware2_class
        parent_mock.consumer = test_event_consumer

        self.event_middleware_receiver.add_middleware_definition(test_middleware1_class)
        self.event_middleware_receiver.add_middleware_definition(test_middleware2_class)
        self.event_middleware_receiver.receive(test_event, test_event_consumer)

        parent_mock.assert_has_calls(
            [
                call.middleware1_class().before_consume(test_event, test_event_consumer),
                call.middleware2_class().before_consume(test_event, test_event_consumer),
                call.consumer.consume(test_event),
                call.middleware2_class().after_consume(test_event, test_event_consumer),
                call.middleware1_class().after_consume(test_event, test_event_consumer),
            ]
        )
