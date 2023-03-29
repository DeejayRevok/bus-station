from contextvars import copy_context
from unittest import TestCase
from uuid import UUID, uuid4

from bus_station.command_terminal.command import Command
from bus_station.shared_terminal.distributed import (
    clear_context_distributed_id,
    create_distributed_id,
    get_context_distributed_id,
    get_distributed_id,
)


class TestCommand(Command):
    pass


class TestDistributed(TestCase):
    def setUp(self) -> None:
        clear_context_distributed_id()

    def test_create_distributed_id(self):
        create_distributed_id()

        context = copy_context()
        context_vars = list(context.items())
        self.assertEqual("bus_station_distributed_id", context_vars[0][0].name)
        try:
            UUID(context_vars[0][1])
        except Exception:
            self.fail("Distributed id is not a valid uuid")

    def test_get_context_distributed_id(self):
        created_distributed_id = create_distributed_id()

        context_distributed_id = get_context_distributed_id()

        self.assertEqual(created_distributed_id, context_distributed_id)

    def test_get_distributed_id_from_passenger(self):
        test_distributed_id = str(uuid4())
        test_passenger = TestCommand()
        test_passenger.set_distributed_id(test_distributed_id)

        distributed_id = get_distributed_id(test_passenger)

        self.assertEqual(test_distributed_id, distributed_id)
        self.assertEqual(get_context_distributed_id(), test_distributed_id)

    def test_get_distributed_id_from_context(self):
        created_distributed_id = create_distributed_id()
        test_passenger = TestCommand()

        distributed_id = get_distributed_id(test_passenger)

        self.assertEqual(created_distributed_id, distributed_id)

    def test_get_distributed_id_new(self):
        test_passenger = TestCommand()

        distributed_id = get_distributed_id(test_passenger)

        context_distributed_id = get_context_distributed_id()
        self.assertEqual(context_distributed_id, distributed_id)

    def test_clear_context_distributed_id(self):
        create_distributed_id()

        clear_context_distributed_id()

        context_distributed_id = get_context_distributed_id()
        self.assertIsNone(context_distributed_id)
