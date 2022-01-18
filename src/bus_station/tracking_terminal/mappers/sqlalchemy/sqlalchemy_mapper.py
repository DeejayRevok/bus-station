from abc import ABC, abstractmethod
from typing import Type

from sqlalchemy import MetaData, Table
from sqlalchemy.orm import mapper


class SQLAlchemyMapper(ABC):
    def __init__(self, db_metadata: MetaData):
        self._db_metadata = db_metadata

    @property
    @abstractmethod
    def model(self) -> Type:
        pass

    @property
    @abstractmethod
    def _proxy(self) -> Type:
        pass

    @property
    @abstractmethod
    def table(self) -> Table:
        pass

    def map(self) -> None:
        mapper(self._proxy, self.table)
