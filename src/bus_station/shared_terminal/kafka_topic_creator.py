from typing import Final, Set

from confluent_kafka import KafkaError, KafkaException
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic  # pyre-ignore[21]


class KafkaTopicCreator:
    __DEFAULT_PARTITIONS_NUMBER: Final = 4

    def __init__(self, kafka_admin_client: AdminClient):
        self.__admin_client = kafka_admin_client
        self.__topics_created: Set = set()

    def create(self, topic: str) -> None:
        if topic in self.__topics_created:
            return

        topic_creation_futures = self.__admin_client.create_topics(
            [NewTopic(topic, self.__DEFAULT_PARTITIONS_NUMBER)]  # pyre-ignore[16]
        )
        try:
            topic_creation_futures[topic].result()
        except KafkaException as ex:
            kafka_error = ex.args[0]
            if kafka_error.code() != KafkaError.TOPIC_ALREADY_EXISTS:
                raise ex

        self.__topics_created.add(topic)
