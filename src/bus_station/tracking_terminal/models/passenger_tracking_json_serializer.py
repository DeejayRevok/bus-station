from dataclasses import asdict
from datetime import datetime
from json import dumps

from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking
from bus_station.tracking_terminal.models.passenger_tracking_serializer import PassengerTrackingSerializer


class PassengerTrackingJSONSerializer(PassengerTrackingSerializer):
    def serialize(self, passenger_tracking: PassengerTracking) -> str:
        tracking_data_dict = asdict(passenger_tracking)
        for tracking_data_key, tracking_data_value in tracking_data_dict.items():
            if isinstance(tracking_data_value, datetime):
                tracking_data_dict[tracking_data_key] = tracking_data_value.isoformat()
        return dumps(tracking_data_dict)
