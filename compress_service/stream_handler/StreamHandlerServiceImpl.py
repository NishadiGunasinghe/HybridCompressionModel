import hashlib
import json
import logging
import random
import time
import uuid

import boto3

from config.Configuration import Configuration
from stream_handler.StreamHandlerService import StreamHandlerService

logger = logging.getLogger(__name__)


class StreamHandlerServiceImpl(StreamHandlerService):

    def __init__(self):
        if Configuration.AWS_ACCESS_KEY and Configuration.AWS_SECRET_KEY:
            self.kinesis_client = boto3.client("kinesis",
                                               endpoint_url=Configuration.AWS_ENDPOINT_OVERRIDE,
                                               region_name=Configuration.AWS_REGION,
                                               aws_access_key_id=Configuration.AWS_ACCESS_KEY,
                                               aws_secret_access_key=Configuration.AWS_SECRET_KEY)
            self.sqs_client = boto3.client("sqs",
                                           endpoint_url=Configuration.AWS_ENDPOINT_OVERRIDE,
                                           region_name=Configuration.AWS_REGION,
                                           aws_access_key_id=Configuration.AWS_ACCESS_KEY,
                                           aws_secret_access_key=Configuration.AWS_SECRET_KEY)
        else:
            self.kinesis_client = boto3.client("kinesis",
                                               endpoint_url=Configuration.AWS_ENDPOINT_OVERRIDE,
                                               region_name=Configuration.AWS_REGION)
            self.sqs_client = boto3.client("sqs",
                                           endpoint_url=Configuration.AWS_ENDPOINT_OVERRIDE,
                                           region_name=Configuration.AWS_REGION)
        self.stream_name = Configuration.STREAM_NAME
        self.file_upload_sequence = []

    def put(self, chunk_data: bytes, file_name: str, chunk_number: int, total_chunks: int, metadata):
        if Configuration.ENABLE_DATA_PUSH:
            logger.info("Data has been added to the given service")
            logger.info(f"List All Streams: {self.kinesis_client.list_streams()} ")
            partition_key = hashlib.md5(file_name.encode('utf-8')).hexdigest()
            # Introduce a random delay between 0.1 and 1.0 seconds
            delay = random.uniform(0.1, 1.0)
            time.sleep(delay)
            result = self.kinesis_client.put_record(
                StreamName=self.stream_name,
                Data=chunk_data,
                PartitionKey=partition_key
            )
            self.file_upload_sequence.append(result["SequenceNumber"])
            logger.info(
                f"Data added to Kinesis: {result} check is addition to sqs [{chunk_number}: {total_chunks}] = [{chunk_number == total_chunks - 1}]")
            if chunk_number == total_chunks - 1:
                data_metadata = {
                    "ID": str(uuid.uuid4()),
                    "file_name": file_name,
                    "file_total_chunk": int(total_chunks),
                    "shard_id": result["ShardId"],
                    "sequence_number": sorted(self.file_upload_sequence),
                    "metadata": json.dumps(metadata)
                }
                sqs_message = self.sqs_client.send_message(QueueUrl=Configuration.SQS_FIFO_QUEUE,
                                                           MessageBody=json.dumps(data_metadata),
                                                           MessageGroupId=data_metadata["shard_id"],
                                                           MessageDeduplicationId=data_metadata["ID"])
                logger.info(f"Added the data [{sqs_message}]")
                self.file_upload_sequence = []

    def get_data_from_sqs(self, queue_url):
        # Receive a message from the SQS queue
        response = self.sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,  # Change to 10 to process multiple messages at once
            VisibilityTimeout=0,  # Time to process the message before it's visible again
            WaitTimeSeconds=20  # Long polling for up to 20 seconds
        )
        messages = response.get('Messages', [])
        if messages:
            # Extract the message
            message = messages[0]
            receipt_handle = message['ReceiptHandle']
            body = message['Body']

            # Process the message (for example, parse JSON)
            message_data = json.loads(body)
            logger.info("Message received:", message_data)

            return message_data["file_name"], receipt_handle

        return None, None

    def delete(self, queue_url, receipt_handle):
        self.sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
