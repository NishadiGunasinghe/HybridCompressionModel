import bz2
import lzma

from compressor import CompressionLibraryService
from compressor.CompressionLibraryOptions import CompressionLibraryOptions
from config.Configuration import Configuration
from stream_handler.StreamHandlerService import StreamHandlerService
from report_generator.CompressionReport import generatev2
from compressor.CompressionLibraryServiceImpl import CompressionLibraryServiceImpl
from file_handler.FileHandler import FileHandler
from stream_handler.StreamHandlerServiceImpl import StreamHandlerServiceImpl


def start_app():
    special_character = Configuration.SPECIAL_DIVIDER_CHARACTER
    stream_size_kb = Configuration.STREAM_FILE_BREAK_SIZE_KB  # Change this to your desired stream size in KB
    source_directory = Configuration.READ_LOCATION  # Change this to your source directory
    filename = Configuration.RESULT_FILE_NAME

    comp_lib_service: CompressionLibraryService = CompressionLibraryServiceImpl(special_character, stream_size_kb)
    _register_compression_functions(comp_lib_service)
    stream_handler_service: StreamHandlerService = StreamHandlerServiceImpl()
    file_handler = FileHandler(source_directory, comp_lib_service, stream_size_kb, stream_handler_service)
    data_report = file_handler.process()
    if Configuration.ENABLE_REPORT:
        string_report_content = generatev2(data_report)
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
