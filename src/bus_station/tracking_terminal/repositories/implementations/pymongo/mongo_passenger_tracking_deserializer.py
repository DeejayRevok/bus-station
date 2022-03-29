from datetime import datetime
from typing import Optional, Type

from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking


class MongoPassengerTrackingDeserializer:
    def deserialize(
        self, serialized_tracking_data: dict, target_tracking_class: Type[PassengerTracking]
    ) -> PassengerTracking:
        id_value = serialized_tracking_data.pop("_id")
        serialized_tracking_data["id"] = id_value
        serialized_tracking_data["execution_start"] = self.__deserialize_timestamp(
            serialized_tracking_data["execution_start"]
        )
        serialized_tracking_data["execution_end"] = self.__deserialize_timestamp(
            serialized_tracking_data["execution_end"]
        )
        return target_tracking_class(**serialized_tracking_data)

    def __deserialize_timestamp(self, timestamp: Optional[float]) -> Optional[datetime]:
        if timestamp is None:
            return None
        return datetime.fromtimestamp(timestamp)
