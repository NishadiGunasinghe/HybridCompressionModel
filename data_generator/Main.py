import logging

from FileHandler import FileHandler
from config.Configuration import Configuration

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('apscheduler').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


def start_app():
    logger.info("Data Generator started")
    logger.info(f"Queue configuration {Configuration.SQS_FIFO_QUEUE}")
    file_handler = FileHandler()

    while True:
        file_handler.handle_file()


if __name__ == "__main__":
    start_app()
