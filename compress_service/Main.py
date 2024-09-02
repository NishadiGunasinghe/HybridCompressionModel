import bz2
import logging
import threading
import time

import zstd
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from compressor import CompressionLibraryService
from compressor.CompressionLibraryOptions import CompressionLibraryOptions
from compressor.CompressionLibraryServiceImpl import CompressionLibraryServiceImpl
from config.Configuration import Configuration
from file_handler.FileHandler import FileHandler
from report_generator.CompressionReport import generatev2
from stream_handler.StreamHandlerService import StreamHandlerService
from stream_handler.StreamHandlerServiceImpl import StreamHandlerServiceImpl

# Create a lock object
task_lock = threading.Lock()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('apscheduler').setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)


def start_app():
    logger.info("Application started")
    special_character = Configuration.SPECIAL_DIVIDER_CHARACTER
    stream_size_kb = Configuration.STREAM_FILE_BREAK_SIZE_KB  # Change this to your desired stream size in KB
    source_directory = Configuration.READ_LOCATION  # Change this to your source directory

    comp_lib_service: CompressionLibraryService = CompressionLibraryServiceImpl(special_character, stream_size_kb)
    _register_compression_functions(comp_lib_service)
    stream_handler_service: StreamHandlerService = StreamHandlerServiceImpl()
    file_handler = FileHandler(source_directory, comp_lib_service, stream_size_kb, stream_handler_service)

    # Create a scheduler
    scheduler = BackgroundScheduler()

    # Schedule a task to run every 5 seconds
    scheduler.add_job(func=process_read_file,
                      trigger=IntervalTrigger(seconds=Configuration.SCHEDULAR_TRIGGER_INTERVAL),
                      coalesce=True,
                      args=(file_handler, stream_handler_service))

    # Start the scheduler
    scheduler.start()
    logger.info("Schedular started")
    try:
        # Keep the script running
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Shutdown the scheduler when exiting the app
        scheduler.shutdown()


def process_read_file(file_handler, stream_handler_service):
    with task_lock:
        file_path, receipt_handle = stream_handler_service.get_data_from_sqs(Configuration.FILE_SQS_FIFO_QUEUE)
        if file_path is not None and receipt_handle is not None:
            try:
                data_report = file_handler.process(f"test_location/{file_path}")
                if Configuration.ENABLE_REPORT:
                    string_report_content = generatev2(data_report)
                append_to_file(Configuration.RESULT_FILE_NAME, string_report_content)
                stream_handler_service.delete(Configuration.FILE_SQS_FIFO_QUEUE, receipt_handle)
            except FileNotFoundError:
                logger.error(f"An error occurred given file is not available {file_path}")
        else:
            logger.info("No messages")


def append_to_file(filename, content):
    with open(filename, 'a') as file:  # 'a' mode opens the file for appending
        file.write(content + '\n')  # Append content with a newline


def _register_compression_functions(comp_lib_service: CompressionLibraryService):
    comp_lib_service.register(bz2.compress, bz2.decompress,
                              CompressionLibraryOptions(name='bz2', order=1, compresslevel=2))
    comp_lib_service.register(zstd.compress, zstd.decompress,
                              CompressionLibraryOptions(name='zstd', order=2))


if __name__ == "__main__":
    start_app()
