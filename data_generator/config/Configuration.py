from os import environ


class Configuration:
    FILE_NAME_PREFIX = environ.get("FILE_NAME_PREFIX", "robotic_data_positions")
    SCHEMA_REF_NUMBER = environ.get("SCHEMA_REF_NUMBER", 2)
    MAX_FILE_SIZE = environ.get("MAX_FILE_SIZE", 25)
    AWS_ENDPOINT_OVERRIDE = environ.get("AWS_ENDPOINT_OVERRIDE", "http://localhost:4566")
    AWS_REGION = environ.get("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY = environ.get("AWS_ACCESS_KEY", "your_access_key")
    AWS_SECRET_KEY = environ.get("AWS_SECRET_KEY", "your_secret_key")
    SQS_FIFO_QUEUE = environ.get("SQS_FIFO_QUEUE", "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/aws-file-sqs.fifo")