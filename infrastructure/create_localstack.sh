#!/bin/bash

echo "Waiting for LocalStack to start..."
sleep 10

awslocal --endpoint-url=http://localhost:4566 kinesis create-stream --stream-name aws-stream-compressor-kinesis-service --shard-count 10;

awslocal --endpoint-url=http://localhost:4566 kinesis list-streams;

if awslocal sqs list-queues | grep -q aws-stream-compressor-sqs-dlq.fifo; then
  echo "aws-stream-compressor-sqs-dlq.fifo already exists!"
else
  DLQ_QUEUE_URL=$(awslocal sqs create-queue --queue-name aws-stream-compressor-sqs-dlq.fifo --attributes FifoQueue=true --output json | grep -o '"QueueUrl": "[^"]*' | awk -F'"' '{print $4}')
  echo "Created DLQ: $DLQ_QUEUE_URL!"
fi

if awslocal sqs list-queues | grep -q aws-stream-compressor-sqs.fifo; then
  echo "aws-stream-compressor-sqs.fifo already exists!"
else
  SQS_QUEUE_URL=$(awslocal sqs create-queue --queue-name aws-stream-compressor-sqs.fifo --attributes FifoQueue=true --output json | grep -o '"QueueUrl": "[^"]*' | awk -F'"' '{print $4}')
  DLQ_QUEUE_ARN=$DLQ_QUEUE_URL

  awslocal sqs set-queue-attributes --queue-url $SQS_QUEUE_URL \
  --attributes "{\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"$DLQ_QUEUE_ARN\\\",\\\"maxReceiveCount\\\":\\\"5\\\"}\"}"

  awslocal sqs set-queue-attributes --queue-url $SQS_QUEUE_URL --attributes DeduplicationScope=queue

  echo "Created SQS Queue: $SQS_QUEUE_URL!"
fi


if awslocal sqs list-queues | grep -q aws-file-sqs-dlq.fifo; then
  echo "aws-file-sqs-dlq.fifo already exists!"
else
  DLQ_QUEUE_URL=$(awslocal sqs create-queue --queue-name aws-file-sqs-dlq.fifo --attributes FifoQueue=true --output json | grep -o '"QueueUrl": "[^"]*' | awk -F'"' '{print $4}')
  echo "Created DLQ: $DLQ_QUEUE_URL!"
fi

if awslocal sqs list-queues | grep -q aws-file-sqs.fifo; then
  echo "aws-file-sqs.fifo already exists!"
else
  SQS_QUEUE_URL=$(awslocal sqs create-queue --queue-name aws-file-sqs.fifo --attributes FifoQueue=true --output json | grep -o '"QueueUrl": "[^"]*' | awk -F'"' '{print $4}')
  DLQ_QUEUE_ARN=$DLQ_QUEUE_URL

  awslocal sqs set-queue-attributes --queue-url $SQS_QUEUE_URL \
  --attributes "{\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"$DLQ_QUEUE_ARN\\\",\\\"maxReceiveCount\\\":\\\"5\\\"}\"}"

  awslocal sqs set-queue-attributes --queue-url $SQS_QUEUE_URL --attributes DeduplicationScope=queue

  echo "Created SQS Queue: $SQS_QUEUE_URL!"
fi


# Add more commands here as needed
