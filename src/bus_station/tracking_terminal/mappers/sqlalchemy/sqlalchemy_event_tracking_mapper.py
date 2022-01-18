from typing import Type

from sqlalchemy import Table, Column, String, JSON, DateTime

from bus_station.tracking_terminal.mappers.sqlalchemy.sqlalchemy_mapper import SQLAlchemyMapper
from bus_station.tracking_terminal.models.event_tracking import EventTracking
from bus_station.tracking_terminal.models.proxy_definitions import SAEventTrackingProxy


class SQLAlchemyEventTrackingMapper(SQLAlchemyMapper):
    @property
    def table(self) -> Table:
        return Table(
            "event_tracking",
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
        return EventTracking

    @property
    def _proxy(self) -> Type:
        return SAEventTrackingProxy
