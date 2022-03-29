from typing import Type

from sqlalchemy import JSON, Column, DateTime, String, Table

from bus_station.tracking_terminal.mappers.sqlalchemy.sqlalchemy_mapper import SQLAlchemyMapper
from bus_station.tracking_terminal.models.proxy_definitions import SAQueryTrackingProxy
from bus_station.tracking_terminal.models.query_tracking import QueryTracking


class SQLAlchemyQueryTrackingMapper(SQLAlchemyMapper):
    @property
    def table(self) -> Table:
        return Table(
            "query_tracking",
            self._db_metadata,
            Column("id", String(255), primary_key=True),
            Column("name", String(255), nullable=False),
            Column("executor_name", String(255), nullable=False),
            Column("data", JSON, nullable=False),
            Column("response_data", JSON, nullable=True),
            Column("execution_start", DateTime, nullable=False),
            Column("execution_end", DateTime, nullable=True),
        )

    @property
    def model(self) -> Type:
        return QueryTracking

    @property
    def _proxy(self) -> Type:
        return SAQueryTrackingProxy
