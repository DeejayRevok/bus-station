from dataclasses import asdict
from datetime import datetime
from typing import Optional

from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking


class MongoPassengerTrackingSerializer:
    def serialize(self, tracking_instance: PassengerTracking) -> dict:
        instance_data = asdict(tracking_instance)
        id_value = instance_data.pop("id")
        instance_data["_id"] = id_value
        instance_data["execution_start"] = self.__serialize_date_time(tracking_instance.execution_start)
        instance_data["execution_end"] = self.__serialize_date_time(tracking_instance.execution_end)
        return instance_data

    def __serialize_date_time(self, date_time: Optional[datetime]) -> Optional[float]:
        if date_time is None:
            return None
        return date_time.timestamp()
