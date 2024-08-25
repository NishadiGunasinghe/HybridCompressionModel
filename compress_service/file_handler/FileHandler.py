import base64
import csv
import io
import json
import os

from PIL import Image

from Util import _FILE, _UNCOMPRESSED_FILE_SIZE, _FILE_SUMMARY, _COMPRESSION_NAME, \
    _FILE_COMPRESSED_TIME, \
    _COMPRESSED_CHUNK_SIZE, _UNCOMPRESSED_CHUNK_SIZE, _CHUNK_COMPRESSED_TIME, _COMPRESSED_FILE_SIZE, _FIRST_COMPRESSION, \
    _SECOND_COMPRESSION
from compressor.CompressionLibraryService import CompressionLibraryService
from stream_handler.StreamHandlerService import StreamHandlerService


class FileHandler:

    def __init__(self, folder_location, comp_lib_service: CompressionLibraryService, stream_size_kb,
                 stream_handler_service: StreamHandlerService):
        self.folder_location = folder_location
        self.comp_lib_service = comp_lib_service
        self.chunk_size_bytes = stream_size_kb * 1024
        self.stream_handler_service: StreamHandlerService = stream_handler_service

    def process(self):
        file_paths = self.get_all_file_paths()
        folder_summary = []
        # Get the file extension
        for file_path in file_paths:
            if 'delete' not in file_path:
                print(f"[START] {file_path} Processing started")
                _, ext = os.path.splitext(file_path)
                # Read file content based on file type
                if ext.lower() == '.csv':
                    content = self.read_csv(file_path)
                elif ext.lower() == '.json':
                    content = self.read_json(file_path)
                elif ext.lower() == '.txt':
                    content = self.read_text(file_path)
                elif ext.lower() == '.jpg':
                    content = self.read_image(file_path)
                else:
                    print(f"Unsupported file type: {ext}")
                    return
                print(f"[END] {file_path} Processing completed and file sie is {len(content) / (1024 * 1024)} MB")
                # Stream content in chunks
                chunk_summary = self.chunk_compressor(content, file_path)
                file_summary = {
                    _FILE: file_path,
                    _UNCOMPRESSED_FILE_SIZE: len(content),
                    _FILE_SUMMARY: chunk_summary
                }
                folder_summary.append(file_summary)
            else:
                print(f"Ignore the compression since file already deleted {file_path}")

        return folder_summary

    def get_all_file_paths(self):
        # List to store all file paths
        file_paths = []

        # Walk through the directory
        for root, directories, files in os.walk(self.folder_location):
            for filename in files:
                # Join the two strings to form the full file path.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)

        return file_paths

    def read_csv(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            return self.string_to_bytes('\n'.join([','.join(row) for row in reader]))

    def read_json(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            return self.string_to_bytes(json.dumps(json.load(file), separators=(',', ':')))

    def read_text(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            return ' '.join(file.read().split()).encode('utf-8')

    def read_image(self, file_path):
        with Image.open(file_path) as img:
            # Create a BytesIO object to hold the image data
            img_byte_arr = io.BytesIO()
            # Save the image to the BytesIO object in the original format
            img.save(img_byte_arr, format=img.format)
            # Get the byte data
            byte_data = img_byte_arr.getvalue()
            return byte_data

    def string_to_bytes(self, string):
        return string.encode("utf-8")

    def chunk_compressor(self, content, file_path):
        # Convert the text to bytes
        # Calculate the number of chunks
        total_bytes = len(content)
        num_chunks = (total_bytes + self.chunk_size_bytes - 1) // self.chunk_size_bytes

        if num_chunks <= 1:
            compressed_data_1, compressed_summary = self.comp_lib_service.compress(content, 0)
            self.stream_handler_service.put(compressed_data_1, file_path, 0, num_chunks, {
                _COMPRESSION_NAME: compressed_summary[0][_COMPRESSION_NAME]
            })
            return {
                _COMPRESSION_NAME: compressed_summary[0][_COMPRESSION_NAME],
                _COMPRESSED_FILE_SIZE: compressed_summary[0][_COMPRESSED_CHUNK_SIZE],
                _UNCOMPRESSED_FILE_SIZE: compressed_summary[0][_UNCOMPRESSED_CHUNK_SIZE],
                _FILE_COMPRESSED_TIME: compressed_summary[0][_CHUNK_COMPRESSED_TIME]
            }

        combined_file = []
        first_compression_data_set = []
        overall_summary = {
            _FIRST_COMPRESSION: {
                _COMPRESSION_NAME: "",
                _COMPRESSED_FILE_SIZE: 0.0,
                _UNCOMPRESSED_FILE_SIZE: 0.0,
                _FILE_COMPRESSED_TIME: 0.0
            },
            _SECOND_COMPRESSION: {
                _COMPRESSION_NAME: "",
                _COMPRESSED_FILE_SIZE: 0.0,
                _UNCOMPRESSED_FILE_SIZE: 0.0,
                _FILE_COMPRESSED_TIME: 0.0
            }
        }
        # Loop through and process each chunk
        for i in range(num_chunks):
            start = i * self.chunk_size_bytes
            end = min(start + self.chunk_size_bytes, total_bytes)
            chunk = content[start:end]
            # Convert chunk back to string if needed
            compressed_data_1, compressed_summary = self.comp_lib_service.compress(chunk, 0)
            first_compression_data_set.append(compressed_data_1)
            base64_encoded_data = base64.b64encode(compressed_data_1).decode('utf-8')
            combined_file.append(base64_encoded_data)
            overall_summary[_FIRST_COMPRESSION][_COMPRESSION_NAME] = compressed_summary[0][_COMPRESSION_NAME]
            overall_summary[_FIRST_COMPRESSION][_COMPRESSED_FILE_SIZE] = overall_summary[_FIRST_COMPRESSION][
                                                                             _COMPRESSED_FILE_SIZE] + \
                                                                         compressed_summary[0][
                                                                             _COMPRESSED_CHUNK_SIZE]
            overall_summary[_FIRST_COMPRESSION][_UNCOMPRESSED_FILE_SIZE] = overall_summary[_FIRST_COMPRESSION][
                                                                               _UNCOMPRESSED_FILE_SIZE] + \
                                                                           compressed_summary[0][
                                                                               _UNCOMPRESSED_CHUNK_SIZE]
            overall_summary[_FIRST_COMPRESSION][_FILE_COMPRESSED_TIME] = overall_summary[_FIRST_COMPRESSION][
                                                                             _FILE_COMPRESSED_TIME] + \
                                                                         compressed_summary[0][
                                                                             _CHUNK_COMPRESSED_TIME]

        combined_value = '|'.join(combined_file)
        if len(combined_value) >= self.chunk_size_bytes:
            total_bytes = len(combined_value)
            num_chunks = (total_bytes + self.chunk_size_bytes - 1) // self.chunk_size_bytes

            for i in range(num_chunks):
                start = i * self.chunk_size_bytes
                end = min(start + self.chunk_size_bytes, total_bytes)
                chunk = self.string_to_bytes(combined_value[start:end])
                # Convert chunk back to string if needed
                compressed_data_2, compressed_summary = self.comp_lib_service.compress(chunk, 1)
                overall_summary[_SECOND_COMPRESSION][_COMPRESSION_NAME] = compressed_summary[0][_COMPRESSION_NAME]
                overall_summary[_SECOND_COMPRESSION][_COMPRESSED_FILE_SIZE] = overall_summary[_SECOND_COMPRESSION][
                                                                                  _COMPRESSED_FILE_SIZE] + \
                                                                              compressed_summary[0][
                                                                                  _COMPRESSED_CHUNK_SIZE]
                overall_summary[_SECOND_COMPRESSION][_UNCOMPRESSED_FILE_SIZE] = overall_summary[_SECOND_COMPRESSION][
                                                                                    _UNCOMPRESSED_FILE_SIZE] + \
                                                                                compressed_summary[0][
                                                                                    _UNCOMPRESSED_CHUNK_SIZE]
                overall_summary[_SECOND_COMPRESSION][_FILE_COMPRESSED_TIME] = overall_summary[_SECOND_COMPRESSION][
                                                                                  _FILE_COMPRESSED_TIME] + \
                                                                              compressed_summary[0][
                                                                                  _CHUNK_COMPRESSED_TIME]

                self.stream_handler_service.put(compressed_data_2, file_path, i, num_chunks, {
                    _COMPRESSION_NAME: overall_summary[_SECOND_COMPRESSION][_COMPRESSION_NAME]
                })

        else:
            del overall_summary[_SECOND_COMPRESSION]
            for first_compression_data_chunk in first_compression_data_set:
                self.stream_handler_service.put(first_compression_data_chunk, file_path, 0, num_chunks, {
                    _COMPRESSION_NAME: overall_summary[_FIRST_COMPRESSION][_COMPRESSION_NAME]
                })

        self.mark_as_processed_file(file_path)
        return overall_summary

    def mark_as_processed_file(self, file_path):
        self.rename_file_before_extension(file_path, "_delete")
        print("Delete Completed")

    def rename_file_before_extension(self, file_path, insert_string):
        # Split the file path into the name and the extension
        base_name, extension = os.path.splitext(file_path)
        # Create the new file name by inserting the string before the extension
        new_file_path = f"{base_name}{insert_string}{extension}"
        # Rename the file
        os.rename(file_path, new_file_path)
        return new_file_path
