# Hybrid Compression Model

> Hybrid compression model is a high-performance library for real-time text data streaming using advanced compression techniques.
> It reduces bandwidth and storage requirements while maintaining data integrity.
> Ideal for data analytics, IoT, and real-time monitoring applications,
> This optimizes data flow for efficiency and reliability.

## What services includes here

01. compress_service
02. data_generator
03. decompress_service

#### Compress Service

> This service retrieves JSON, TXT, and CSV data from the specified location and subsequently compresses these files
> using
> the LZMA and BZ2 algorithms.
> Additionally, it reads data from an SQS first-in-first-out (FIFO) queue and includes a
> scheduler program that triggers every second.
> To ensure that the service waits until a job is completed, a locking
> mechanism has been implemented.

#### Data Generator

> This service will read a schema file and generate approximately 1MB of data, simulating the behavior of a service that
> receives data from various streaming and non-streaming sources. It will then create data files in a specified location
> and place the data into an SQS first-in-first-out (FIFO) queue.

#### Decompress Service

> This service retrieves data from the streaming data location and subsequently decompresses these files using
> the LZMA and BZ2 algorithms.
> Additionally, it reads data from an SQS first-in-first-out (FIFO) queue and includes a
> scheduler program that triggers every second.
> To ensure that the service waits until a job is completed, a locking
> mechanism has been implemented.

#### Service Design Diagram

![Service Design Diagram!](/docs/product%20idea%20design%20graph.png "Service Design Diagram")

#### Prototype Implementation Diagram

![Prototype Implementation Diagram!](/docs/research_extended-local-product.png "Prototype Implementation Diagram")

---

## Start development & local setup

1. Install Python into your PC: [Python Installation](https://www.python.org/downloads)
2. Create ```.venv``` in the parent directory ```stream-compress``` or in the submodules
   ```shell 
    python -m venv .
   ```
3. Install all the dependencies 
   ```shell
    pip install -r requirements.txt
   ```
4. Start each application 
   ```shell 
   python Main.py
   ```
5. Start localstack refer "Start docker compose service"
   
## Start docker compose service

1. Install docker service [Docker Installation](https://docs.docker.com/desktop/install/windows-install)
2. Start localstack using the following command & this will create the relevant resources to verify whether it is created or not
   ```shell
   docker compose up localstak -d
   ```
3. Start other services 
   ```shell
   docker compose up -d
   ```

## Environment variables for each service 

### Compress Service

| Variable                   | Default Value                                                                                       |
|----------------------------|-----------------------------------------------------------------------------------------------------|
| SPECIAL_DIVIDER_CHARACTER  | \|                                                                                                  |
| STREAM_FILE_BREAK_SIZE_KB  | 400                                                                                                 |
| READ_LOCATION              | "test_location"                                                                                     |
| AWS_ENDPOINT_OVERRIDE      | "http://localhost:4566"                                                                             |
| AWS_REGION                 | "us-east-1"                                                                                         |
| AWS_ACCESS_KEY             | "your_access_key"                                                                                   |
| AWS_SECRET_KEY             | "your_access_key"                                                                                   |
| STREAM_NAME                | "aws-stream-compressor-kinesis-service"                                                             |
| RESULT_FILE_NAME           | "reports/results.html"                                                                              |
| SQS_FIFO_QUEUE             | "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/aws-stream-compressor-sqs.fifo"  |
| FILE_SQS_FIFO_QUEUE        | "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/aws-file-sqs.fifo"               |
| ENABLE_DATA_PUSH           | False                                                                                               |
| ENABLE_REPORT              | True                                                                                                |
| COMPRESSED_REPORT          | True                                                                                                |
| SCHEDULAR_TRIGGER_INTERVAL | 1                                                                                                   |

### Data Generator Service

| Variable              | Default Value                                                                         |
|-----------------------|---------------------------------------------------------------------------------------|
| FILE_NAME_PREFIX      | "stock_market_data"                                                                   |
| SCHEMA_REF_NUMBER     | 2                                                                                     |
| MAX_FILE_SIZE         | 25                                                                                    |
| AWS_ENDPOINT_OVERRIDE | "http://localhost:4566"                                                               |
| AWS_REGION            | "us-east-1"                                                                           |
| AWS_ACCESS_KEY        | "your_access_key"                                                                     |
| AWS_SECRET_KEY        | "your_access_key"                                                                     |
| SQS_FIFO_QUEUE        | "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/aws-file-sqs.fifo" |

### Decompress Service

| Variable                   | Default Value                                                                                       |
|----------------------------|-----------------------------------------------------------------------------------------------------|
| SPECIAL_DIVIDER_CHARACTER  | \|                                                                                                  |
| STREAM_FILE_BREAK_SIZE_KB  | 400                                                                                                 |
| READ_LOCATION              | "test_location"                                                                                     |
| AWS_ENDPOINT_OVERRIDE      | "http://localhost:4566"                                                                             |
| AWS_REGION                 | "us-east-1"                                                                                         |
| AWS_ACCESS_KEY             | "your_access_key"                                                                                   |
| AWS_SECRET_KEY             | "your_access_key"                                                                                   |
| STREAM_NAME                | "aws-stream-compressor-kinesis-service"                                                             |
| RESULT_FILE_NAME           | "reports/results.html"                                                                              |
| SQS_FIFO_QUEUE             | "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/aws-stream-compressor-sqs.fifo"  |
| SCHEDULAR_TRIGGER_INTERVAL | 1                                                                                                   |
