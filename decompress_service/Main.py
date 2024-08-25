import base64
import bz2
import lzma

from config.Configuration import Configuration
from decompressor import CompressionLibraryService
from decompressor.CompressionLibraryOptions import CompressionLibraryOptions
from decompressor.CompressionLibraryServiceImpl import CompressionLibraryServiceImpl
from stream_handler.StreamHandlerService import StreamHandlerService
from stream_handler.StreamHandlerServiceImpl import StreamHandlerServiceImpl


def start_app():
    special_character = Configuration.SPECIAL_DIVIDER_CHARACTER
    stream_size_kb = Configuration.STREAM_FILE_BREAK_SIZE_KB  # Change this to your desired stream size in KB

    comp_lib_service: CompressionLibraryService = CompressionLibraryServiceImpl(special_character, stream_size_kb)
    _register_compression_functions(comp_lib_service)

    stream_handler_service: StreamHandlerService = StreamHandlerServiceImpl()
    data_set, compression_also = stream_handler_service.get()

    if data_set and compression_also:
        decompression_order = split_and_trim(compression_also)
        first_level_decompressed_data_set = []
        middle_level_decode = []
        final_decompression_set = []
        #decompression
        for item in data_set:
            decompressed = comp_lib_service.decompress(item, decompression_order[0])
            first_level_decompressed_data_set.append(bytes_to_string(decompressed))

        first_level_decompressed_data = ''.join(first_level_decompressed_data_set)
        first_level_decompressed_data_set = first_level_decompressed_data.split("|")

        for file in first_level_decompressed_data_set:
            base64_encoded_data = base64.b64decode(file)
            middle_level_decode.append(base64_encoded_data)

        for file in middle_level_decode:
            final_decompression_set.append(bytes_to_string(comp_lib_service.decompress(file, decompression_order[1])))

        print("Final File\n\n\n")
        print(f"{''.join(final_decompression_set)}")

def bytes_to_string(byte_sequence):
    return ''.join(chr(byte) for byte in byte_sequence)

def split_and_trim(algorithm_order):
    # Split the string by '+'
    parts = algorithm_order.split('+')
    # Strip whitespace from each part
    trimmed_parts = [part.strip() for part in parts]
    reversed_list = trimmed_parts[::-1]
    return reversed_list

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
