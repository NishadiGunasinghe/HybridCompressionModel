import logging
import time

from Util import _DECOMPRESSION_NAME, _COMPRESSION_ORDER, _COMPRESSION_FUNC, _DECOMPRESSION_FUNC, \
    _FUNC_OPTIONS, _COMPRESSED_CHUNK_SIZE, _DECOMPRESSED_CHUNK_SIZE, \
    _CHUNK_DECOMPRESSED_TIME
from decompressor import CompressionLibraryOptions
from decompressor.CompressionLibraryService import CompressionLibraryService, validate

logger = logging.getLogger(__name__)


class CompressionLibraryServiceImpl(CompressionLibraryService):

    def __init__(self, special_character, chunk_size):
        self.override_final_file = None
        self.compressed_data = None
        self.decompressed_data = None
        self.chunk_size = chunk_size
        self.special_character = special_character
        self.compression_libs = []
        self.combined_file = []

    def register(self, compression_func, decompression_func, options: CompressionLibraryOptions):
        validate(options)
        name = options.get_attr(_DECOMPRESSION_NAME)
        order = options.get_attr(_COMPRESSION_ORDER)
        options.remove_attr(_DECOMPRESSION_NAME)
        options.remove_attr(_COMPRESSION_ORDER)
        if options.has_attributes():
            self.compression_libs.append(
                {
                    _DECOMPRESSION_NAME: name,
                    _COMPRESSION_FUNC: compression_func,
                    _DECOMPRESSION_FUNC: decompression_func,
                    _COMPRESSION_ORDER: order,
                    _FUNC_OPTIONS: options
                }
            )
        else:
            self.compression_libs.append(
                {
                    _DECOMPRESSION_NAME: name,
                    _COMPRESSION_FUNC: compression_func,
                    _DECOMPRESSION_FUNC: decompression_func,
                    _COMPRESSION_ORDER: order,
                    _FUNC_OPTIONS: None
                }
            )

    def compress(self, uncompressed_data: bytes, compression_algo_number: int):
        pass

    def decompress(self, compressed_data: bytes, compression_algo_name: str):
        # Use a list comprehension to find the dictionary
        decompress_data_detail = []
        decompression_func = [item for item in self.compression_libs if item['name'] == compression_algo_name]
        start_time = time.time()
        decompressed_data = decompression_func[0][_DECOMPRESSION_FUNC](compressed_data)
        total_decompress_time = time.time() - start_time
        decompress_data_detail.append({
            _DECOMPRESSION_NAME: compression_algo_name,
            _DECOMPRESSED_CHUNK_SIZE: len(decompressed_data),
            _COMPRESSED_CHUNK_SIZE: len(compressed_data),
            _CHUNK_DECOMPRESSED_TIME: total_decompress_time,
            _COMPRESSION_ORDER: None
        })
        logging.info(
            f"Chunk decompression completed func {compression_algo_name} and time taken {total_decompress_time}")
        return decompressed_data, decompress_data_detail
