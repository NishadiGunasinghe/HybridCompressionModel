import datetime
import json
import os
import random
import string
import sys

from config.Configuration import Configuration


class FileHandler:
    main_type_array = ['FeatureCollection', 'RoundCollection', 'SquireCollection', 'TriangleCollection',
                       'TestCollection']
    type_array = ['Round', 'Squire', 'Triangle', 'Hexagon', 'Pentagon']

    # Function to generate random data based on type
    def generate_data(self, schema):
        schema["type"] = random.choice(self.main_type_array)
        for item in schema["features"]:
            type = random.choice(self.type_array)
            item["properties"]["name"] = type
            item["id"] = type[:2].upper()
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
        filename = f"data/{Configuration.FILE_NAME_PREFIX}_{timestamp}.json"
        return filename

    def handle_file(self):
        schema = self.load_schema(f"{os.getcwd()}/json_schema_ref/schema_{Configuration.SCHEMA_REF_NUMBER}.json")
        generated_data = self.generate_data(schema)
        output_file = self.generate_filename()
        self.save_data(output_file, generated_data)
        print(
            f"Generated data saved to {output_file} with size approximately {len(generated_data) / (1024 * 1024)} MB.")
