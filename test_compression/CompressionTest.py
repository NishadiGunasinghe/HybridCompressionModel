import bz2
import gzip
import lzma
import zlib

import brotli
import zstd
import lz4.frame

from compression_manger import CompressionLibraryService
from compression_manger.CompressionLibraryOptions import CompressionLibraryOptions
from test_compression.compression_algo_report_generator.CompressionReport import generatev2
from test_compression.compression_manager.CompressionTestLibraryServiceImpl import CompressionTestLibraryServiceImpl
from test_compression.file_manager.FileHandler import FileHandler


def start_app():
    special_character = "|"
    stream_size_kb = 400  # Change this to your desired stream size in KB
    comp_lib_service: CompressionLibraryService = CompressionTestLibraryServiceImpl(special_character, stream_size_kb)
    _register_compression_functions(comp_lib_service)
    source_directory = 'test_location'  # Change this to your source directory
    file_handler = FileHandler(source_directory, comp_lib_service, stream_size_kb)
    data_report = file_handler.process()
    string_report_content = generatev2(data_report)
    filename = 'results.txt'
    append_to_file(filename, string_report_content)


def append_to_file(filename, content):
    with open(filename, 'a') as file:  # 'a' mode opens the file for appending
        file.write(content + '\n')  # Append content with a newline


def _register_compression_functions(comp_lib_service: CompressionLibraryService):
    comp_lib_service.register(
        bz2.compress, bz2.decompress, CompressionLibraryOptions(name='bz2', order=1, compresslevel=2)
    )
    comp_lib_service.register(
        lzma.compress, lzma.decompress,
        CompressionLibraryOptions(name='lzma', order=3, format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64,
                                  preset=lzma.PRESET_DEFAULT, filters=None)
    )


if __name__ == "__main__":
    start_app()
