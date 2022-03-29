from unittest import TestCase
from unittest.mock import Mock

from kombu import Connection, Consumer, Message, Queue
from kombu.transport.virtual import Channel

from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor
from bus_station.passengers.passenger import Passenger
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.bus_stop import BusStop


class TestPassengerKombuConsumer(TestCase):
    def setUp(self) -> None:
        self.connection_mock = Mock(spec=Connection)
        self.queue_mock = Mock(spec=Queue)
        self.bus_stop_mock = Mock(spec=BusStop)
        self.class_mock = Passenger
        self.middleware_executor_mock = Mock(spec=PassengerMiddlewareExecutor)
        self.deserializer_mock = Mock(spec=PassengerDeserializer)
        self.passenger_kombu_consumer = PassengerKombuConsumer(
            self.connection_mock,
            self.queue_mock,
            self.bus_stop_mock,
            self.class_mock,
            self.middleware_executor_mock,
            self.deserializer_mock,
        )

    def test_get_consumers(self):
        test_consumer = Mock(spec=Consumer)
        test_consumer_class_mock = Mock(spec=Consumer.__class__)
        test_consumer_class_mock.return_value = test_consumer
        test_channel_mock = Mock(spec=Channel)

        consumers = self.passenger_kombu_consumer.get_consumers(test_consumer_class_mock, test_channel_mock)

        self.assertCountEqual([test_consumer], consumers)
        test_consumer_class_mock.assert_called_with(
            queues=[self.queue_mock], callbacks=[self.passenger_kombu_consumer.on_message]
        )

    def test_on_message_success(self):
        test_passenger = Mock(spec=Passenger)
        self.deserializer_mock.deserialize.return_value = test_passenger
        test_message_mock = Mock(spec=Message)
        test_body = "test_body"

        self.passenger_kombu_consumer.on_message(test_body, test_message_mock)

        self.deserializer_mock.deserialize.assert_called_once_with(test_body, passenger_cls=self.class_mock)
        self.middleware_executor_mock.execute.assert_called_once_with(test_passenger, self.bus_stop_mock)
        test_message_mock.ack.assert_called_once_with()
        test_message_mock.reject.assert_not_called()

    def test_on_message_error(self):
        test_passenger = Mock(spec=Passenger)
        self.deserializer_mock.deserialize.return_value = test_passenger
        test_message_mock = Mock(spec=Message)
        test_body = "test_body"
        self.middleware_executor_mock.execute.side_effect = Exception("test_exception")

        self.passenger_kombu_consumer.on_message(test_body, test_message_mock)

        self.deserializer_mock.deserialize.assert_called_once_with(test_body, passenger_cls=self.class_mock)
        self.middleware_executor_mock.execute.assert_called_once_with(test_passenger, self.bus_stop_mock)
        test_message_mock.ack.assert_not_called()
        test_message_mock.reject.assert_called_once_with(requeue=False)
