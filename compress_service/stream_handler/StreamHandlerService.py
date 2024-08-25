from abc import ABC, abstractmethod


class StreamHandlerService(ABC):

    @abstractmethod
    def put(self, chunk_data: bytes, file_name: str, chunk_number: int, total_chunks: int, metadata):
        pass
