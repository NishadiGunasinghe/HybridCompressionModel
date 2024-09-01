import base64
import json
import logging
import os

from Util import _FIRST_DECOMPRESSION, _SECOND_DECOMPRESSION, _DECOMPRESSION_NAME, _DECOMPRESSED_FILE_SIZE, \
    _COMPRESSED_FILE_SIZE, _FILE_DECOMPRESSED_TIME, _DECOMPRESSED_CHUNK_SIZE, _COMPRESSED_CHUNK_SIZE, \
    _CHUNK_DECOMPRESSED_TIME
from config.Configuration import Configuration
from decompressor import CompressionLibraryService
from report_generator.CompressionReport import generatev2
from stream_handler import StreamHandlerService

logger = logging.getLogger(__name__)


class FileHandler:

    def __init__(self, comp_lib_service: CompressionLibraryService, stream_handler_service: StreamHandlerService):
        self.comp_lib_service = comp_lib_service
        self.stream_handler_service = stream_handler_service

    def process_file(self):
        overall_summary = {
            _FIRST_DECOMPRESSION: {
                _DECOMPRESSION_NAME: "",
                _DECOMPRESSED_FILE_SIZE: 0.0,
                _COMPRESSED_FILE_SIZE: 0.0,
                _FILE_DECOMPRESSED_TIME: 0.0
            },
            _SECOND_DECOMPRESSION: {
                _DECOMPRESSION_NAME: "",
                _DECOMPRESSED_FILE_SIZE: 0.0,
                _COMPRESSED_FILE_SIZE: 0.0,
                _FILE_DECOMPRESSED_TIME: 0.0
            }
        }

        data_set, compression_algo, receipt_handle, file_name = self.stream_handler_service.get_message_sqs()
        if data_set is not None and compression_algo is not None:
            first_level_decompressed_data_set = []
            final_decompression_set = []
            if '+' in compression_algo:
                decompression_order = self.split_and_trim(compression_algo)
                middle_level_decode = []
                # decompression
                # first level de compression
                for item in data_set:
                    decompressed, decompressed_summary = self.comp_lib_service.decompress(item, decompression_order[0])
                    first_level_decompressed_data_set.append(self.bytes_to_string(decompressed))
                    overall_summary[_FIRST_DECOMPRESSION][_DECOMPRESSION_NAME] = decompressed_summary[0][
                        _DECOMPRESSION_NAME]
                    overall_summary[_FIRST_DECOMPRESSION][_DECOMPRESSED_FILE_SIZE] = \
                        overall_summary[_FIRST_DECOMPRESSION][_DECOMPRESSED_FILE_SIZE] + decompressed_summary[0][
                            _DECOMPRESSED_CHUNK_SIZE]
                    overall_summary[_FIRST_DECOMPRESSION][_COMPRESSED_FILE_SIZE] = \
                        overall_summary[_FIRST_DECOMPRESSION][_COMPRESSED_FILE_SIZE] + decompressed_summary[0][
                            _COMPRESSED_CHUNK_SIZE]
                    overall_summary[_FIRST_DECOMPRESSION][_FILE_DECOMPRESSED_TIME] = \
                        overall_summary[_FIRST_DECOMPRESSION][_FILE_DECOMPRESSED_TIME] + decompressed_summary[0][
                            _CHUNK_DECOMPRESSED_TIME]
                first_level_decompressed_data = ''.join(first_level_decompressed_data_set)
                first_level_decompressed_data_set = first_level_decompressed_data.split("|")

                for file in first_level_decompressed_data_set:
                    base64_encoded_data = base64.b64decode(file)
                    middle_level_decode.append(base64_encoded_data)

                for file in middle_level_decode:
                    # second level de compression
                    decompressed, decompressed_summary = self.comp_lib_service.decompress(file, decompression_order[1])
                    final_decompression_set.append(self.bytes_to_string(decompressed))

                    overall_summary[_SECOND_DECOMPRESSION][_DECOMPRESSION_NAME] = decompressed_summary[0][
                        _DECOMPRESSION_NAME]
                    overall_summary[_SECOND_DECOMPRESSION][_DECOMPRESSED_FILE_SIZE] = \
                        overall_summary[_SECOND_DECOMPRESSION][_DECOMPRESSED_FILE_SIZE] + decompressed_summary[0][
                            _DECOMPRESSED_CHUNK_SIZE]
                    overall_summary[_SECOND_DECOMPRESSION][_COMPRESSED_FILE_SIZE] = \
                        overall_summary[_SECOND_DECOMPRESSION][_COMPRESSED_FILE_SIZE] + decompressed_summary[0][
                            _COMPRESSED_CHUNK_SIZE]
                    overall_summary[_SECOND_DECOMPRESSION][_FILE_DECOMPRESSED_TIME] = \
                        overall_summary[_SECOND_DECOMPRESSION][_FILE_DECOMPRESSED_TIME] + decompressed_summary[0][
                            _CHUNK_DECOMPRESSED_TIME]


            else:
                del overall_summary[_SECOND_DECOMPRESSION]
                compression_algo = compression_algo.strip()
                for item in data_set:
                    decompressed, decompressed_summary = self.comp_lib_service.decompress(item, compression_algo)
                    first_level_decompressed_data_set.append(self.bytes_to_string(decompressed))
                    overall_summary[_FIRST_DECOMPRESSION][_DECOMPRESSION_NAME] = decompressed_summary[0][
                        _DECOMPRESSION_NAME]
                    overall_summary[_FIRST_DECOMPRESSION][_DECOMPRESSED_FILE_SIZE] = \
                        overall_summary[_FIRST_DECOMPRESSION][_DECOMPRESSED_FILE_SIZE] + decompressed_summary[0][
                            _DECOMPRESSED_CHUNK_SIZE]
                    overall_summary[_FIRST_DECOMPRESSION][_COMPRESSED_FILE_SIZE] = \
                        overall_summary[_FIRST_DECOMPRESSION][_COMPRESSED_FILE_SIZE] + decompressed_summary[0][
                            _COMPRESSED_CHUNK_SIZE]
                    overall_summary[_FIRST_DECOMPRESSION][_FILE_DECOMPRESSED_TIME] = \
                        overall_summary[_FIRST_DECOMPRESSION][_FILE_DECOMPRESSED_TIME] + decompressed_summary[0][
                            _CHUNK_DECOMPRESSED_TIME]

                for item in first_level_decompressed_data_set:
                    final_decompression_set.append(item)

            logger.info("Send the data to file creation\n\n\n")
            self.write_data(''.join(final_decompression_set), file_name)
            logger.info("File created and sending message handler to delete message from sqs")
            self.stream_handler_service.delete_sqs_message(receipt_handle)
            logger.info("File decompression completed")
            string_report_content = generatev2(overall_summary, file_name)
            self.append_to_file(Configuration.RESULT_FILE_NAME, string_report_content)
        else:
            logger.info("No message")

    def bytes_to_string(self, byte_sequence):
        return ''.join(chr(byte) for byte in byte_sequence)

    def write_data(self, data_set, file_name):
        # Get the file name with extension
        file_name_with_extension = os.path.basename(file_name)
        # Split the file name and extension
        file_name, file_extension = os.path.splitext(file_name_with_extension)
        with open(f"decompressed_data/{file_name}{file_extension}", 'w') as file:
            json.dump(json.loads(data_set), file)
            file.flush()

    def append_to_file(self, filename, content):
        with open(filename, 'a') as file:  # 'a' mode opens the file for appending
            file.write(content + '\n')  # Append content with a newline

    def split_and_trim(self, algorithm_order):
        # Split the string by '+'
        parts = algorithm_order.split('+')
        # Strip whitespace from each part
        trimmed_parts = [part.strip() for part in parts]
        reversed_list = trimmed_parts[::-1]
        return reversed_list
