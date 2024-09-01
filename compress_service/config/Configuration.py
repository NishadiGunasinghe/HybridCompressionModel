from os import environ


class Configuration:
    SPECIAL_DIVIDER_CHARACTER = environ.get("SPECIAL_DIVIDER_CHARACTER", "|")
    STREAM_FILE_BREAK_SIZE_KB = environ.get("STREAM_FILE_BREAK_SIZE_KB", 400)
    READ_LOCATION = environ.get("READ_LOCATION", "test_location")
    AWS_ENDPOINT_OVERRIDE = environ.get("AWS_ENDPOINT_OVERRIDE", "http://localhost:4566")
    AWS_REGION = environ.get("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY = environ.get("AWS_ACCESS_KEY", "your_access_key")
    AWS_SECRET_KEY = environ.get("AWS_SECRET_KEY", "your_secret_key")
    STREAM_NAME = environ.get("STREAM_NAME", "aws-stream-compressor-kinesis-service")
    RESULT_FILE_NAME = environ.get("RESULT_FILE_NAME", "reports/results.html")
    SQS_FIFO_QUEUE = environ.get("SQS_FIFO_QUEUE", "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/aws-stream-compressor-sqs.fifo")
    FILE_SQS_FIFO_QUEUE = environ.get("SQS_FIFO_QUEUE", "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/aws-file-sqs.fifo")
    ENABLE_DATA_PUSH = environ.get("ENABLE_DATA_PUSH", False)
    ENABLE_REPORT = environ.get("ENABLE_REPORT", True)
    COMPRESSED_REPORT = environ.get("COMPRESSED_REPORT", True)
    SCHEDULAR_TRIGGER_INTERVAL = environ.get("SCHEDULAR_TRIGGER_INTERVAL", 1)
