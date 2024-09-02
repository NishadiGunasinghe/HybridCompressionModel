from abc import abstractmethod
from abc import ABC

from compressor import CompressionLibraryOptions


def validate(options: CompressionLibraryOptions):
    if options is None:
        raise TypeError("Options cannot be empty")
    elif options.get_attr('name') is None:
        raise TypeError("Name cannot be empty")
    elif options.get_attr('order') is None:
        raise TypeError("Order cannot be empty")


class CompressionLibraryService(ABC):

    @abstractmethod
    def register(self, compression_func, decompression_func, options: CompressionLibraryOptions):
        pass

    @abstractmethod
    def compress(self, uncompressed_data: bytes, compression_algo_number: int):
        pass
