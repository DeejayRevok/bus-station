from unittest import TestCase

import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import clear_mappers

from bus_station.tracking_terminal.mappers.sqlalchemy.sqlalchemy_command_tracking_mapper import (
    SQLAlchemyCommandTrackingMapper,
)


@pytest.mark.usefixtures("postgres")
class TestSQLAlchemyCommandTrackingMapper(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_env_ready = False
        cls.postgres_user = cls.postgres["user"]
        cls.postgres_password = cls.postgres["password"]
        cls.postgres_host = cls.postgres["host"]
        cls.postgres_port = cls.postgres["port"]
        cls.postgres_db = cls.postgres["db"]
        cls.sqlalchemy_engine = create_engine(
            f"postgresql://{cls.postgres_user}:{cls.postgres_password}"
            f"@{cls.postgres_host}:{cls.postgres_port}/{cls.postgres_db}"
        )
        cls.test_env_ready = True

    def setUp(self) -> None:
        if self.test_env_ready is False:
            self.fail("Test environment is not ready")
        self.sqlalchemy_metadata = MetaData(bind=self.sqlalchemy_engine)
        clear_mappers()
        self.sqlalchemy_command_tracking_mapper = SQLAlchemyCommandTrackingMapper(db_metadata=self.sqlalchemy_metadata)

    def tearDown(self) -> None:
        self.sqlalchemy_metadata.drop_all()

    def test_map(self):
        self.sqlalchemy_command_tracking_mapper.map()

        table_names = self.sqlalchemy_metadata.tables.keys()
        self.assertIn("command_tracking", table_names)
