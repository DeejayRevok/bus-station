from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class QueryResponse:
    data: Optional[Any]
