from __future__ import annotations

from typing import Final

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient

from bus_station.shared_terminal.kafka_topic_creator import KafkaTopicCreator
from bus_station.tracking_terminal.models.passenger_model_tracking_map import PassengerModelTrackingMap
from bus_station.tracking_terminal.models.passenger_tracking_json_serializer import PassengerTrackingJSONSerializer
from bus_station.tracking_terminal.models.passenger_tracking_serializer import PassengerTrackingSerializer
from bus_station.tracking_terminal.trackers.kafka_passenger_tracker import KafkaPassengerTracker


class KafkaPassengerTrackerBuilder:
    __DEFAULT_KAFKA_CONFIG: Final = {"queue.buffering.max.ms": 10}
    __DEFAULT_PASSENGER_TRACKING_SERIALIZER: Final = PassengerTrackingJSONSerializer()
    __DEFAULT_PASSENGER_MODEL_TRACKING_MAP: Final = PassengerModelTrackingMap()

    def __init__(self, kafka_bootstrap_servers: str):
        self.__kafka_bootstrap_servers = kafka_bootstrap_servers
        self.__kafka_config = self.__DEFAULT_KAFKA_CONFIG
        self.__passenger_tracking_serializer = self.__DEFAULT_PASSENGER_TRACKING_SERIALIZER
        self.__passenger_model_tracking_map = self.__DEFAULT_PASSENGER_MODEL_TRACKING_MAP

    def with_kafka_config(self, kafka_config: dict) -> KafkaPassengerTrackerBuilder:
        self.__kafka_config = kafka_config
        return self

    def with_passenger_tracking_serializer(
        self, passenger_tracking_serializer: PassengerTrackingSerializer
    ) -> KafkaPassengerTrackerBuilder:
        self.__passenger_tracking_serializer = passenger_tracking_serializer
        return self

    def with_passenger_model_tracking_map(
        self, passenger_model_tracking_map: PassengerModelTrackingMap
    ) -> KafkaPassengerTrackerBuilder:
        self.__passenger_model_tracking_map = passenger_model_tracking_map
        return self

    def build(self, client_id: str) -> KafkaPassengerTracker:
        kafka_producer = Producer(
            {"bootstrap.servers": self.__kafka_bootstrap_servers, "client.id": client_id, **self.__kafka_config}
        )
        kafka_topic_creator = KafkaTopicCreator(AdminClient({"bootstrap.servers": self.__kafka_bootstrap_servers}))
        return KafkaPassengerTracker(
            kafka_producer=kafka_producer,
            kafka_topic_creator=kafka_topic_creator,
            passenger_tracking_serializer=self.__passenger_tracking_serializer,
            passenger_model_tracking_map=self.__passenger_model_tracking_map,
        )
