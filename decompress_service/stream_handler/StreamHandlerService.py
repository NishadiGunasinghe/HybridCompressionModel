from abc import ABC, abstractmethod


class StreamHandlerService(ABC):

    @abstractmethod
    def get(self):
        pass
