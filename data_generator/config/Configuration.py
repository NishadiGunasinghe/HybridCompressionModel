from os import environ


class Configuration:
    FILE_NAME_PREFIX = environ.get("FILE_NAME_PREFIX", "stock_market_data")
    SCHEMA_REF_NUMBER = environ.get("SCHEMA_REF_NUMBER", 1)
    MAX_FILE_SIZE = environ.get("MAX_FILE_SIZE", 25)

