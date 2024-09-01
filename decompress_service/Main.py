import bz2
import logging
import lzma
import threading
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config.Configuration import Configuration
from decompressor import CompressionLibraryService
from decompressor.CompressionLibraryOptions import CompressionLibraryOptions
from decompressor.CompressionLibraryServiceImpl import CompressionLibraryServiceImpl
from file_handler.FileHandler import FileHandler
from stream_handler.StreamHandlerService import StreamHandlerService
from stream_handler.StreamHandlerServiceImpl import StreamHandlerServiceImpl

# Create a lock object
task_lock = threading.Lock()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('apscheduler').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


def start_app():
    special_character = Configuration.SPECIAL_DIVIDER_CHARACTER
    stream_size_kb = Configuration.STREAM_FILE_BREAK_SIZE_KB  # Change this to your desired stream size in KB

    comp_lib_service: CompressionLibraryService = CompressionLibraryServiceImpl(special_character, stream_size_kb)
    _register_compression_functions(comp_lib_service)

    stream_handler_service: StreamHandlerService = StreamHandlerServiceImpl()

    # Create a scheduler
    scheduler = BackgroundScheduler()
    file_handler = FileHandler(comp_lib_service, stream_handler_service)

    # Schedule a task to run every 5 seconds
    scheduler.add_job(func=process_file,
                      trigger=IntervalTrigger(seconds=Configuration.SCHEDULAR_TRIGGER_INTERVAL),
                      coalesce=True,
                      args=(file_handler, "Started execution"))
    # Start the scheduler
    scheduler.start()
    logger.info("Schedular started")
    try:
        # Keep the script running
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit) as error:
        # Shutdown the scheduler when exiting the app
        logger.error(f"Stopped {error}")
        scheduler.shutdown()


def process_file(file_handler: FileHandler, message: str):
    logger.info(f"{message}")
    with task_lock:
        file_handler.process_file()


def _register_compression_functions(comp_lib_service: CompressionLibraryService):
    comp_lib_service.register(
        lzma.compress, lzma.decompress,
        CompressionLibraryOptions(name='lzma', order=1, format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64,
                                  preset=lzma.PRESET_DEFAULT, filters=None)
    )
    comp_lib_service.register(
        bz2.compress, bz2.decompress, CompressionLibraryOptions(name='bz2', order=2, compresslevel=2)
    )


if __name__ == "__main__":
    start_app()
