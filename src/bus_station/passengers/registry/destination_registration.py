from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from bus_station.shared_terminal.bus_stop import BusStop


@dataclass(frozen=True)
class DestinationRegistration:
    destination: Optional[BusStop]
    destination_contact: Any