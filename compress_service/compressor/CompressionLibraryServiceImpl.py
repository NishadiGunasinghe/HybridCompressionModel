import time

from Util import _COMPRESSION_NAME, _COMPRESSION_ORDER, _COMPRESSION_FUNC, _DECOMPRESSION_FUNC, \
    _FUNC_OPTIONS, _COMPRESSED_CHUNK_SIZE, _UNCOMPRESSED_CHUNK_SIZE, _CHUNK_COMPRESSED_TIME
from compressor import CompressionLibraryOptions
from compressor.CompressionLibraryService import CompressionLibraryService, validate


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
        name = options.get_attr(_COMPRESSION_NAME)
        order = options.get_attr(_COMPRESSION_ORDER)
        options.remove_attr(_COMPRESSION_NAME)
        options.remove_attr(_COMPRESSION_ORDER)
        if options.has_attributes():
            self.compression_libs.append(
                {
                    _COMPRESSION_NAME: name,
                    _COMPRESSION_FUNC: compression_func,
                    _DECOMPRESSION_FUNC: decompression_func,
                    _COMPRESSION_ORDER: order,
                    _FUNC_OPTIONS: options
                }
            )
        else:
            self.compression_libs.append(
                {
                    _COMPRESSION_NAME: name,
                    _COMPRESSION_FUNC: compression_func,
                    _DECOMPRESSION_FUNC: decompression_func,
                    _COMPRESSION_ORDER: order,
                    _FUNC_OPTIONS: None
                }
            )

    def compress(self, uncompressed_data: bytes, compression_algo_number: int):

        compression_libs = sorted(self.compression_libs, key=lambda x: x[_COMPRESSION_ORDER])
        compress_data_detail = []
        if len(compression_libs) > 2:
            raise TypeError("More compression are configured")
        compression_func = compression_libs[compression_algo_number]

        # second compression type
        start_time = time.time()
        if compression_func[_FUNC_OPTIONS].get_dict() is not None:
            options = compression_func[_FUNC_OPTIONS].get_dict()
            compressed_data = compression_func[_COMPRESSION_FUNC](uncompressed_data, **options)
        else:
            compressed_data = compression_func[_COMPRESSION_FUNC](uncompressed_data)
        total_compress_time = time.time() - start_time

        algo_name = ""
        if compression_algo_number == 1:
            algo_name = f"{compression_libs[0][_COMPRESSION_NAME]} + {compression_func[_COMPRESSION_NAME]}"
        else:
            algo_name = f"{compression_func[_COMPRESSION_NAME]}"

        compress_data_detail.append({
            _COMPRESSION_NAME: algo_name,
            _COMPRESSED_CHUNK_SIZE: len(compressed_data),
            _UNCOMPRESSED_CHUNK_SIZE: len(uncompressed_data),
            _CHUNK_COMPRESSED_TIME: total_compress_time,
            _COMPRESSION_ORDER: None
        })
        return compressed_data, compress_data_detail

    def decompress(self, compressed_data: bytes):
        pass
