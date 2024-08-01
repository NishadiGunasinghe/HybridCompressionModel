import gzip

import lz4.frame

from compression_manger.CompressionLibraryOptions import CompressionLibraryOptions
from compression_manger.CompressionLibraryService import CompressionLibraryService
from compression_manger.CompressionLibraryServiceImpl import CompressionLibraryServiceImpl
from file_manger.StreamHandler import monitor_folder


def start_app():
    comp_lib_service: CompressionLibraryService = CompressionLibraryServiceImpl()
    _register_compression_functions(comp_lib_service)

    source_directory = 'data_location'  # Change this to your source directory
    target_directory = 'delete_data_location'  # Change this to your target directory
    stream_size_kb = 450  # Change this to your desired stream size in KB
    monitor_folder(source_directory, target_directory, stream_size_kb, comp_lib_service)


def _register_compression_functions(comp_lib_service: CompressionLibraryService):
    comp_lib_service.register(
        lz4.frame.compress, lz4.frame.decompress, CompressionLibraryOptions(name='lz4', order=2)
    )
    comp_lib_service.register(
        gzip.compress, gzip.decompress, CompressionLibraryOptions(name='gzip', order=1)
    )


if __name__ == "__main__":
    start_app()
