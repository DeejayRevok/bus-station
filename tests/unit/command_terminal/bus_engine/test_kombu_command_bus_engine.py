from unittest import TestCase
from unittest.mock import Mock, patch

from kombu import Connection, Exchange, Queue
from kombu.transport.virtual import Channel

from bus_station.command_terminal.bus_engine.kombu_command_bus_engine import KombuCommandBusEngine
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_not_found import CommandHandlerNotFound
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer


class TestKombuCommandBusEngine(TestCase):
    def setUp(self) -> None:
        self.broker_connection_mock = Mock(spec=Connection)
        self.channel_mock = Mock(spec=Channel)
        self.broker_connection_mock.channel.return_value = self.channel_mock
        self.command_handler_registry_mock = Mock(spec=CommandHandlerRegistry)
        self.command_receiver_mock = Mock(spec=PassengerReceiver)
        self.command_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.command_type_mock = Mock(spec=Command)

    @patch("bus_station.command_terminal.bus_engine.kombu_command_bus_engine.Queue")
    @patch("bus_station.command_terminal.bus_engine.kombu_command_bus_engine.Exchange")
    @patch("bus_station.command_terminal.bus_engine.kombu_command_bus_engine.PassengerKombuConsumer")
    def test_init_handler_not_found(self, consumer_builder_mock, exchange_builder_mock, queue_builder_mock):
        self.command_handler_registry_mock.get_bus_stop_by_name.return_value = None

        with self.assertRaises(CommandHandlerNotFound) as context:
            KombuCommandBusEngine(
                self.broker_connection_mock,
                self.command_handler_registry_mock,
                self.command_receiver_mock,
                self.command_deserializer_mock,
                "test_command_handler",
            )

        self.assertEqual("test_command_handler", context.exception.command_handler_name)
        self.command_handler_registry_mock.get_bus_stop_by_name.assert_called_once_with("test_command_handler")
        consumer_builder_mock.assert_not_called()
        exchange_builder_mock.assert_not_called()
        queue_builder_mock.assert_not_called()

    @patch("bus_station.command_terminal.bus_engine.kombu_command_bus_engine.Queue")
    @patch("bus_station.command_terminal.bus_engine.kombu_command_bus_engine.Exchange")
    @patch("bus_station.command_terminal.bus_engine.kombu_command_bus_engine.PassengerKombuConsumer")
    def test_init_handler_found(self, consumer_builder_mock, exchange_builder_mock, queue_builder_mock):
        test_queue = Mock(spec=Queue)
        queue_builder_mock.return_value = test_queue
        test_exchange = Mock(spec=Exchange)
        exchange_builder_mock.return_value = test_exchange
        test_command_handler = Mock(spec=CommandHandler)
        self.command_handler_registry_mock.get_bus_stop_by_name.return_value = test_command_handler
        test_command = Mock(spec=Command)
        test_command.passenger_name.return_value = "test_command"
        test_command_handler.passenger.return_value = test_command

        KombuCommandBusEngine(
            self.broker_connection_mock,
            self.command_handler_registry_mock,
            self.command_receiver_mock,
            self.command_deserializer_mock,
            "test_command_handler",
        )

        test_exchange.declare.assert_called_once_with()
        queue_builder_mock.assert_called_once_with(
            name="test_command",
            queue_arguments={"x-dead-letter-exchange": "failed_commands"},
        )
        test_queue.declare.assert_called_once_with(channel=self.channel_mock)
        consumer_builder_mock.assert_called_once_with(
            self.broker_connection_mock,
            test_queue,
            test_command_handler,
            test_command,
            self.command_receiver_mock,
            self.command_deserializer_mock,
        )

    @patch("bus_station.command_terminal.bus_engine.kombu_command_bus_engine.Queue")
    @patch("bus_station.command_terminal.bus_engine.kombu_command_bus_engine.Exchange")
    @patch("bus_station.command_terminal.bus_engine.kombu_command_bus_engine.PassengerKombuConsumer")
    def test_start(self, consumer_builder_mock, *_):
        test_kombu_consumer = Mock(spec=PassengerKombuConsumer)
        consumer_builder_mock.return_value = test_kombu_consumer
        engine = KombuCommandBusEngine(
            self.broker_connection_mock,
            self.command_handler_registry_mock,
            self.command_receiver_mock,
            self.command_deserializer_mock,
            "test_command",
        )

        engine.start()

        test_kombu_consumer.run.assert_called_once_with()

    @patch("bus_station.command_terminal.bus_engine.kombu_command_bus_engine.Queue")
    @patch("bus_station.command_terminal.bus_engine.kombu_command_bus_engine.Exchange")
    @patch("bus_station.command_terminal.bus_engine.kombu_command_bus_engine.PassengerKombuConsumer")
    def test_stop(self, consumer_builder_mock, *_):
        test_kombu_consumer = Mock(spec=PassengerKombuConsumer)
        consumer_builder_mock.return_value = test_kombu_consumer
        engine = KombuCommandBusEngine(
            self.broker_connection_mock,
            self.command_handler_registry_mock,
            self.command_receiver_mock,
            self.command_deserializer_mock,
            "test_command",
        )

        engine.stop()

        test_kombu_consumer.stop.assert_called_once_with()
