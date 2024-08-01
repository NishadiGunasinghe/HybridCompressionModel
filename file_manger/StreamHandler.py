import os
import time
import shutil
import json
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from compression_manger import CompressionLibraryService


class StreamHandler(FileSystemEventHandler):
    def __init__(self, source_dir, target_dir, stream_size_kb, comp_lib_service: CompressionLibraryService):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.comp_lib_service = comp_lib_service
        self.stream_size_kb = stream_size_kb * 1024  # Convert to bytes

    def process(self, file_path):
        # Get the file extension
        _, ext = os.path.splitext(file_path)
        # Read file content based on file type
        if ext.lower() == '.csv':
            content = self.read_csv(file_path)
        elif ext.lower() == '.json':
            content = self.read_json(file_path)
        elif ext.lower() == '.txt':
            content = self.read_text(file_path)
        else:
            print(f"Unsupported file type: {ext}")
            return
        # Stream content in chunks
        self.stream_compressor(content)
        # Move processed file to target directory
        shutil.move(file_path, os.path.join(self.target_dir, os.path.basename(file_path)))
        print(f"Moved {file_path} to {self.target_dir}")

    def read_csv(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            return '\n'.join([','.join(row) for row in reader])

    def read_json(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            return json.dumps(json.load(file))

    def read_text(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            return file.read()

    def stream_compressor(self, content):
        stream_size = self.stream_size_kb
        for i in range(0, len(content), stream_size):
            start_time = time.time()
            chunk = content[i:i + stream_size]
            data_bytes = chunk.encode('utf-8')
            compressed_data = self.comp_lib_service.compress(data_bytes)
            compression_ratio = len(chunk) / len(compressed_data)
            space_saving = (1 - (len(compressed_data)/len(chunk))) * 100
            total_compress_time = time.time() - start_time
            print("\n\n")
            print(f"Uncompress File size {len(chunk)/1024}")
            print(f"Compress File size {len(compressed_data)/1024}")
            print(f"File Compression Ratio is {compression_ratio}")
            print(f"Total Compression Time {total_compress_time:.6f} seconds")
            print(f"Space saving {space_saving}")

    def on_created(self, event):
        if not event.is_directory:
            self.process(event.src_path)


def monitor_folder(source_dir, target_dir, stream_size_kb, comp_lib_service: CompressionLibraryService):
    event_handler = StreamHandler(source_dir, target_dir, stream_size_kb, comp_lib_service)
    observer = Observer()
    observer.schedule(event_handler, path=source_dir, recursive=False)
    observer.start()
    print(f"Monitoring {source_dir} for new files...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
