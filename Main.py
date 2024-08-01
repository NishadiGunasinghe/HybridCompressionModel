import json
import time
import lz4.frame

from compression_manger.CompressionLibraryOptions import CompressionLibraryOptions
from compression_manger.CompressionLibraryService import CompressionLibraryService

import zlib
import brotli
import zstandard as zstd
import gzip

from compression_manger.CompressionLibraryServiceImpl import CompressionLibraryServiceImpl


def start_app():
    comp_lib_service: CompressionLibraryService = CompressionLibraryServiceImpl()
    # _register_compression_functions(comp_lib_service)

    start_time = time.time()
    with open('data_location/sample_data.json', 'r') as file:
        data = json.dumps(json.load(file))
        data_bytes = data.encode('utf-8')

        # compressed_data = comp_lib_service.compress(data_bytes)
        # compressed_data1 = brotli.compress(data_bytes)
        compressed_data1 = gzip.compress(data_bytes)

        # compressed_data1 = brotli.compress(data_bytes, quality=11, mode=0, lgblock=24, lgwin=22)
        compressed_data = lz4.frame.compress(compressed_data1)

        compression_ratio = len(data_bytes) / len(compressed_data)
        total_compress_time = time.time() - start_time
        print(f"File Compression Ratio is {compression_ratio}")
        print(f"Total Compression Time {total_compress_time}")

        # start_time = time.time()
        # decompressed_data = comp_lib_service.decompress(compressed_data)
        # total_compress_time = time.time() - start_time
        # decompressed_data = decompressed_data.decode('utf-8')
        # print(f"Total Decompression Time {total_compress_time}")


# def _register_compression_functions(comp_lib_service: CompressionLibraryService):
#     # comp_lib_service.register(
#     #     lz4.frame.compress, lz4.frame.decompress, CompressionLibraryOptions(name='lz4', order=2)
#     # )
#     # comp_lib_service.register(
#     #     gzip.compress, gzip.decompress, CompressionLibraryOptions(name='gzip', order=3, compresslevel=8)
#     # )
#     # comp_lib_service.register(
#     #     brotli.compress, brotli.decompress,
#     #     CompressionLibraryOptions(name='brotli', order=1, quality=11, mode=0, lgblock=24, lgwin=22)
#     # )
#     # comp_lib_service.register(
#     #     zstd.ZstdCompressor().compress, zstd.ZstdDecompressor().decompress,
#     #     CompressionLibraryOptions(name='zstd', order=4)
#     # )


if __name__ == "__main__":
    start_app()
