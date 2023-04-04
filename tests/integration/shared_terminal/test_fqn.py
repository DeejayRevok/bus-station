from unittest import TestCase

from bus_station.shared_terminal.fqn import resolve_fqn


class TestFqn(TestCase):
    def test_resolve_fqn_from_instance(self):
        fqn = resolve_fqn(self)

        expected_fqn = "tests.integration.shared_terminal.test_fqn.TestFQN"
        self.assertEqual(expected_fqn, fqn)

    def test_resolve_fqn_from_class(self):
        fqn = resolve_fqn(TestFqn)

        expected_fqn = "tests.integration.shared_terminal.test_fqn.TestFQN"
        self.assertEqual(expected_fqn, fqn)
