import json

from FileHandler import FileHandler


def start_app():
    file_handler = FileHandler()
    while True:
        file_handler.handle_file()


if __name__ == "__main__":
    start_app()
