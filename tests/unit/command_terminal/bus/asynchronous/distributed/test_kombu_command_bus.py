from multiprocessing.context import Process
from unittest import TestCase
from unittest.mock import Mock, patch

from kombu import Connection, Producer, Queue
from kombu.transport.virtual import Channel

from bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus import KombuCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class TestKombuCommandBus(TestCase):
    def setUp(self) -> None:
        self.connection_mock = Mock(spec=Connection)
        self.channel_mock = Mock(spec=Channel)
        self.connection_mock.channel.return_value = self.channel_mock
        self.command_serializer_mock = Mock(spec=PassengerSerializer)
        self.command_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.command_registry_mock = Mock(spec=RemoteCommandRegistry)
        self.command_receiver_mock = Mock(spec=PassengerReceiver[Command, CommandHandler])
        self.kombu_command_bus = KombuCommandBus(
            self.connection_mock,
            self.command_serializer_mock,
            self.command_deserializer_mock,
            self.command_registry_mock,
            self.command_receiver_mock
        )

    def test_transport_not_registered(self):
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_command_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.kombu_command_bus.transport(test_command)

        self.assertEqual(test_command.__class__.__name__, hnffc.exception.command_name)
        self.command_serializer_mock.serialize.assert_not_called()
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with(test_command.__class__)

    @patch("bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus.Process")
    @patch("bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus.Producer")
    def test_receive_success(self, producer_mock, _):
        test_producer = Mock(spec=Producer)
        producer_mock.return_value = test_producer
        test_command = Mock(spec=Command)
        test_command_serialized = "test_command_serialized"
        self.command_serializer_mock.serialize.return_value = test_command_serialized
        self.command_registry_mock.get_commands_registered.return_value = [test_command.__class__]
        self.command_registry_mock.get_command_destination_contact.return_value = test_command.__class__.__name__
        self.kombu_command_bus.start()

        self.kombu_command_bus.transport(test_command)

        self.command_serializer_mock.serialize.assert_called_once_with(test_command)
        test_producer.publish.assert_called_once_with(
            test_command_serialized,
            exchange="",
            routing_key=test_command.__class__.__name__,
            retry=True,
            retry_policy={
                "interval_start": 0,
                "interval_step": 2,
                "interval_max": 10,
                "max_retries": 10,
            },
        )

    @patch("bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus.Producer")
    @patch("bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus.Process")
    @patch("bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus.Queue")
    @patch("bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus.PassengerKombuConsumer")
    def test_start(self, consumer_mock, queue_mock, process_mock, producer_mock):
        test_queue = Mock(spec=Queue)
        queue_mock.return_value = test_queue
        test_consumer = Mock(spec=PassengerKombuConsumer)
        consumer_mock.return_value = test_consumer
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_command_handler = Mock(spec=CommandHandler)
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_commands_registered.return_value = [test_command.__class__]
        self.command_registry_mock.get_command_destination_contact.return_value = test_command.__class__.__name__
        self.command_registry_mock.get_command_destination.return_value = test_command_handler

        self.kombu_command_bus.start()

        queue_mock.assert_called_once_with(
            test_command.__class__.__name__, queue_arguments={"x-dead-letter-exchange": "failed_commands"}
        )
        test_queue.declare.assert_called_once_with(channel=self.channel_mock)
        consumer_mock.assert_called_once_with(
            self.connection_mock,
            test_queue,
            test_command_handler,
            test_command.__class__,
            self.command_receiver_mock,
            self.command_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_consumer.run)
        test_process.start.assert_called_once_with()
        producer_mock.assert_called_once_with(self.channel_mock)

    @patch("bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus.Process")
    @patch("bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus.Queue")
    @patch("bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus.PassengerKombuConsumer")
    def test_stop(self, consumer_mock, queue_mock, process_mock):
        test_queue = Mock(spec=Queue)
        queue_mock.return_value = test_queue
        test_consumer = Mock(spec=PassengerKombuConsumer)
        consumer_mock.return_value = test_consumer
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_command_handler = Mock(spec=CommandHandler)
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_commands_registered.return_value = [test_command.__class__]
        self.command_registry_mock.get_command_destination_contact.return_value = test_command.__class__.__name__
        self.command_registry_mock.get_command_destination.return_value = test_command_handler
        self.kombu_command_bus.start()

        self.kombu_command_bus.stop()

        queue_mock.assert_called_once_with(
            test_command.__class__.__name__, queue_arguments={"x-dead-letter-exchange": "failed_commands"}
        )
        consumer_mock.assert_called_once_with(
            self.connection_mock,
            test_queue,
            test_command_handler,
            test_command.__class__,
            self.command_receiver_mock,
            self.command_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_consumer.run)
        test_consumer.stop.assert_called_once_with()
        test_process.join.assert_called_once_with()
        self.connection_mock.release.assert_called_once_with()
