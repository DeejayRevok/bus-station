from unittest import TestCase
from unittest.mock import MagicMock, Mock

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.rpyc_command_service import RPyCCommandService
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer


class TestRPyCCommandService(TestCase):
    def setUp(self) -> None:
        self.command_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.command_receiver_mock = Mock(spec=PassengerReceiver[Command, CommandHandler])
        self.rpyc_command_service = RPyCCommandService(self.command_deserializer_mock, self.command_receiver_mock)

    def test_register_success(self):
        test_handler = Mock(spec=CommandHandler)
        test_command = Mock(spec=Command)

        self.rpyc_command_service.register(test_command.__class__, test_handler)

        expected_command_callable_name = f"exposed_{test_command.__class__.__name__}"
        self.assertTrue(hasattr(self.rpyc_command_service, expected_command_callable_name))
        rpyc_service_callable = getattr(self.rpyc_command_service, expected_command_callable_name)
        self.assertEqual((test_handler, test_command.__class__), rpyc_service_callable.args)

    def test_command_handling_success(self):
        test_serialized_command = "test_serialized_command"
        test_command = Mock(spec=Command)
        test_command_handler = Mock(spec=CommandHandler)
        self.command_deserializer_mock.deserialize.return_value = test_command

        self.rpyc_command_service.passenger_receiver(
            test_command_handler, test_command.__class__, test_serialized_command
        )

        self.command_deserializer_mock.deserialize.assert_called_once_with(
            test_serialized_command, passenger_cls=test_command.__class__
        )
        self.command_receiver_mock.receive.assert_called_once_with(test_command, test_command_handler)

    def test_command_handling_not_command(self):
        test_not_command = MagicMock()
        test_command_handler = Mock(spec=CommandHandler)
        test_serialized_not_command = "test_serialized_not_command"
        self.command_deserializer_mock.deserialize.return_value = test_not_command

        with self.assertRaises(TypeError):
            self.rpyc_command_service.passenger_receiver(
                test_command_handler, test_not_command.__class__, test_serialized_not_command
            )

        self.command_deserializer_mock.deserialize.assert_called_once_with(
            test_serialized_not_command, passenger_cls=test_not_command.__class__
        )
