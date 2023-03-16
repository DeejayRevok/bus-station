from confluent_kafka import Consumer


class KafkaTestConsumer:
    def __init__(self, consumer: Consumer):
        self.__consumer = consumer
        self.received_message_data = None
        self.running = True

    def consume(self):
        while self.running:
            try:
                message = self.__consumer.poll(1.0)
            except KeyboardInterrupt:
                break

            if message is None:
                continue
            if message.error():
                continue
            self.received_message_data = message.value().decode("utf-8")

        self.__consumer.close()
