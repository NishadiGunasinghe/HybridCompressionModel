import datetime
import json
import logging
import os
import random
import uuid

import boto3

from config.Configuration import Configuration

logger = logging.getLogger(__name__)


class FileHandler:

    def __init__(self):
        if Configuration.AWS_ACCESS_KEY and Configuration.AWS_SECRET_KEY:
            self.sqs_client = boto3.client("sqs",
                                           endpoint_url=Configuration.AWS_ENDPOINT_OVERRIDE,
                                           region_name=Configuration.AWS_REGION,
                                           aws_access_key_id=Configuration.AWS_ACCESS_KEY,
                                           aws_secret_access_key=Configuration.AWS_SECRET_KEY)
        else:
            self.sqs_client = boto3.client("sqs",
                                           endpoint_url=Configuration.AWS_ENDPOINT_OVERRIDE,
                                           region_name=Configuration.AWS_REGION)

    main_type_array = ['FeatureCollection', 'RoundCollection', 'SquireCollection', 'TriangleCollection',
                       'TestCollection']
    type_array = ['Round', 'Squire', 'Triangle', 'Hexagon', 'Pentagon']

    # Function to generate random data based on type
    def generate_data(self, schema: dict):
        schema["type"] = random.choice(self.main_type_array)
        for item in schema["features"]:
            type = random.choice(self.type_array)
            item["properties"]["name"] = type
            item["id"] = type[:2].upper()
        schema["features"] = random.sample(schema["features"], 2)
        logger.info(f"Generated data set size is {len(schema) / (1024 * 1024)}")
        return schema

    def generate_datav2(self, schema: dict):
        schema = random.sample(schema, 5000)
        logger.info(f"Generated data set size is {len(schema)}")
        return schema

    @staticmethod
    def generate_coordinates(num_points=2, range_min=-100, range_max=-1):
        coordinates = []
        for _ in range(num_points):
            x = random.uniform(range_min, range_max)
            y = random.uniform(range_min, range_max)
            coordinates.append([x, y])
        return coordinates

    # Load the schema from the JSON file
    def load_schema(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    # Save the generated data to a JSON file
    def save_data(self, file_path, data):
        with open(file_path, 'w') as file:
            json.dump(data, file)
            file.flush()

    @staticmethod
    def generate_filename():
        # Get the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create the filename with the prefix, timestamp, and .json extension
        filename = f"{Configuration.FILE_NAME_PREFIX}_{timestamp}.json"
        return filename

    def handle_file(self):
        schema = self.load_schema(f"{os.getcwd()}/json_schema_ref/schema_{Configuration.SCHEMA_REF_NUMBER}.json")
        generated_data = self.generate_datav2(schema)
        output_file = self.generate_filename()
        self.save_data(f"data/{output_file}", generated_data)

        data_metadata = {
            "ID": str(uuid.uuid4()),
            "file_name": output_file
        }
       # self.sqs_client.send_message(QueueUrl=Configuration.SQS_FIFO_QUEUE,
        #                             MessageBody=json.dumps(data_metadata),
         #                            MessageGroupId=data_metadata["ID"],
         #                            MessageDeduplicationId=data_metadata["ID"])

        logger.info(
            f"Generated data saved to {output_file} with size approximately {len(generated_data) / (1024 * 1024)} MB. and added to sqs queue")
