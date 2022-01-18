from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PassengerTracking:
    id: str
    name: str
    executor_name: str
    data: dict
    execution_start: Optional[datetime]
    execution_end: Optional[datetime]
