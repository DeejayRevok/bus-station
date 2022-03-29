from typing import Type

from sqlalchemy import JSON, Column, DateTime, String, Table

from bus_station.tracking_terminal.mappers.sqlalchemy.sqlalchemy_mapper import SQLAlchemyMapper
from bus_station.tracking_terminal.models.command_tracking import CommandTracking
from bus_station.tracking_terminal.models.proxy_definitions import SACommandTrackingProxy


class SQLAlchemyCommandTrackingMapper(SQLAlchemyMapper):
    @property
    def table(self) -> Table:
        return Table(
            "command_tracking",
            self._db_metadata,
            Column("id", String(255), primary_key=True),
            Column("name", String(255), nullable=False),
            Column("executor_name", String(255), nullable=False),
            Column("data", JSON, nullable=False),
            Column("execution_start", DateTime, nullable=False),
            Column("execution_end", DateTime, nullable=True),
        )

    @property
    def model(self) -> Type:
        return CommandTracking

    @property
    def _proxy(self) -> Type:
        return SACommandTrackingProxy
