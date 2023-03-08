from confluent_kafka import Producer

from bus_station.shared_terminal.kafka_topic_creator import KafkaTopicCreator
from bus_station.tracking_terminal.models.passenger_model_tracking_map import PassengerModelTrackingMap
from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking
from bus_station.tracking_terminal.models.passenger_tracking_serializer import PassengerTrackingSerializer
from bus_station.tracking_terminal.trackers.passenger_tracker import PassengerTracker


class KafkaPassengerTracker(PassengerTracker):
    def __init__(
        self,
        kafka_producer: Producer,  # pyre-ignore[11]
        kafka_topic_creator: KafkaTopicCreator,
        passenger_tracking_serializer: PassengerTrackingSerializer,
        passenger_model_tracking_map: PassengerModelTrackingMap,
    ):
        super().__init__(passenger_model_tracking_map)
        self.__producer = kafka_producer
        self.__topic_creator = kafka_topic_creator
        self.__passenger_tracking_serializer = passenger_tracking_serializer

    def _track(self, passenger_tracking: PassengerTracking) -> None:
        topic_name = passenger_tracking.__class__.__name__
        self.__topic_creator.create(topic_name)
        self.__producer.produce(
            topic=topic_name, value=self.__passenger_tracking_serializer.serialize(passenger_tracking)
        )
        self.__producer.poll(0)
