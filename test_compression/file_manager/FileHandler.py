import base64
import csv
import io
import json
import os

from PIL import Image

from compression_manger import CompressionLibraryService
from test_compression.Util import _FILE, _UNCOMPRESSED_FILE_SIZE, _FILE_SUMMARY, _COMPRESSION_NAME, \
    _FILE_COMPRESSED_TIME, \
    _COMPRESSED_CHUNK_SIZE, _UNCOMPRESSED_CHUNK_SIZE, _CHUNK_COMPRESSED_TIME, _COMPRESSED_FILE_SIZE, _FIRST_COMPRESSION, \
    _SECOND_COMPRESSION


class FileHandler:

    def __init__(self, folder_location, comp_lib_service: CompressionLibraryService, stream_size_kb):
        self.folder_location = folder_location
        self.comp_lib_service = comp_lib_service
        self.chunk_size_bytes = stream_size_kb * 1024

    def process(self):
        file_paths = self.get_all_file_paths()
        folder_summary = []
        # Get the file extension
        for file_path in file_paths:
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
            chunk_summary = self.chunk_compressor(content)
            file_summary = {
                _FILE: file_path,
                _UNCOMPRESSED_FILE_SIZE: len(content),
                _FILE_SUMMARY: chunk_summary
            }
            folder_summary.append(file_summary)
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
        return bytes([ord(char) for char in string])

    def chunk_compressor(self, content):
        # Convert the text to bytes
        # Calculate the number of chunks
        total_bytes = len(content)
        num_chunks = (total_bytes + self.chunk_size_bytes - 1) // self.chunk_size_bytes

        if num_chunks <= 1:
            compressed_data, compressed_summary = self.comp_lib_service.compress(content, 0)
            return {
                _COMPRESSION_NAME: compressed_summary[0][_COMPRESSION_NAME],
                _COMPRESSED_FILE_SIZE: compressed_summary[0][_COMPRESSED_CHUNK_SIZE],
                _UNCOMPRESSED_FILE_SIZE: compressed_summary[0][_UNCOMPRESSED_CHUNK_SIZE],
                _FILE_COMPRESSED_TIME: compressed_summary[0][_CHUNK_COMPRESSED_TIME]
            }

        combined_file = []
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
            compressed_data, compressed_summary = self.comp_lib_service.compress(chunk, 0)
            base64_encoded_data = base64.b64encode(compressed_data).decode('utf-8')
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

            num_chunks = (total_bytes + self.chunk_size_bytes - 1) // self.chunk_size_bytes

            for i in range(num_chunks):
                start = i * self.chunk_size_bytes
                end = min(start + self.chunk_size_bytes, total_bytes)
                chunk = content[start:end]
                # Convert chunk back to string if needed
                compressed_data, compressed_summary = self.comp_lib_service.compress(chunk, 1)
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
        else:
            del overall_summary[_SECOND_COMPRESSION]
        return overall_summary
