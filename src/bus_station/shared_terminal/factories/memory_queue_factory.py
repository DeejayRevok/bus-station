from multiprocessing import Queue
from typing import Dict


class __MemoryQueueFactory:
    __queues_mapping: Dict[str, Queue] = {}

    def queue_with_id(self, queue_id: str) -> Queue:
        queue = self.__queues_mapping.get(queue_id)
        if queue is None:
            queue = self.__create_queue_for_id(queue_id)
        return queue

    def __create_queue_for_id(self, queue_id: str) -> Queue:
        queue = Queue()
        self.__queues_mapping[queue_id] = queue
        return queue


memory_queue_factory = __MemoryQueueFactory()
