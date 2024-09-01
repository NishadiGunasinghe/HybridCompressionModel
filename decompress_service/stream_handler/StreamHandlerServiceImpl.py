import json
import logging

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

    def get_message_sqs(self):
        try:
            # Receive a message from the SQS queue
            response = self.sqs_client.receive_message(
                QueueUrl=Configuration.SQS_FIFO_QUEUE,
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

                # Get the shard iterator
                shard_iterator = self.kinesis_client.get_shard_iterator(
                    StreamName=Configuration.STREAM_NAME,
                    ShardId=message_data['shard_id'],
                    ShardIteratorType='TRIM_HORIZON'  # You can also use 'TRIM_HORIZON' or other types
                )['ShardIterator']

                data_set = []

                while True:
                    # Get records from the shard
                    records_response = self.kinesis_client.get_records(ShardIterator=shard_iterator)

                    # Process the records
                    records = records_response['Records']
                    ordered_sequence_numbers = message_data["sequence_number"]
                    sequence_set = set(ordered_sequence_numbers)
                    # Filter the data based on the ordered sequence numbers
                    filtered_data = [item for seq_num in ordered_sequence_numbers
                                     for item in records
                                     if item["SequenceNumber"] == seq_num]

                    for record in filtered_data:
                        data_set.append(record['Data'])

                    # Move to the next shard iterator
                    shard_iterator = records_response['NextShardIterator']

                    # If there are no more records, break out of the loop
                    if not records:
                        break

                logger.info(f"All the data got from the kinesis {len(data_set)}")

                return data_set, json.loads(message_data["metadata"])["name"], receipt_handle, message_data["file_name"]
            return None, None, None, None

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return None, None, None, None

    def delete_sqs_message(self, receipt_handle):
        self.sqs_client.delete_message(QueueUrl=Configuration.SQS_FIFO_QUEUE, ReceiptHandle=receipt_handle)
