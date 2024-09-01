from abc import ABC, abstractmethod


class StreamHandlerService(ABC):

    @abstractmethod
    def get_message_sqs(self):
        pass

    def delete_sqs_message(self, handler):
        pass