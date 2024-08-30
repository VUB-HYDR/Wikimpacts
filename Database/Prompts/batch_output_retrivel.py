import argparse
import json
import os
import pathlib
from pathlib import Path

import openai
from dotenv import load_dotenv

from Database.scr.normalize_utils import Logging

if __name__ == "__main__":
    logger = Logging.get_logger("get results from batch processing")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--api_env",
        dest="api_env",
        help="The env file that contains the API keys.",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
        help="The directory where the retrieved LLM outputs will land (as .json)",
        type=str,
    )
    parser.add_argument(
        "-f",
        "--file_name",
        dest="file_name",
        help="The name of the json file in the original article folder",
        type=str,
    )
    parser.add_argument(
        "-b",
        "--raw_dir",
        dest="raw_dir",
        help="The directory where the original file lands (as .json)",
        type=str,
    )
    args = parser.parse_args()
    logger.info(f"Passed args: {args}")
    logger.info(f"Loading {args.raw_dir}")
    pathlib.Path(args.raw_dir).mkdir(parents=True, exist_ok=True)
    file_path = f"{args.raw_dir}/{args.file_name}"
    with open(file_path, "r") as file:
        data = json.load(file)

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    env_path = Path(args.api_env)
    load_dotenv(dotenv_path=env_path)
    client = openai.OpenAI(api_key=os.getenv("API_KEY"))

    # Function to extract message content based on custom_id
    def get_message_by_custom_id(batch_responses, custom_id):
        for response in batch_responses:
            if response.get("custom_id") == custom_id:
                # Extract the message content from the response
                try:
                    message = response["response"]["body"]["choices"][0]["message"]["content"]
                    return message
                except (KeyError, IndexError) as e:
                    return f"Error retrieving message: {str(e)}"
        return f"No response found for custom_id: {custom_id}"

    # Initialize an empty list to store the results
    response = []

    # Retrieve the list of batches
    batches = client.batches.list()

    # Iterate over each batch
    for batch in batches:
        batch_id = batch.id
        output_file_id = batch.output_file_id

        # Retrieve the batch details (if needed)
        client.batches.retrieve(batch_id)

        # Retrieve the file content associated with the output_file_id
        file_response = client.files.content(output_file_id)
        batch_responses = (
            file_response.json()
        )  # get the json error, add the json output in the model setting, and need to check the result /Ni 20240830

        # Iterate over the batch responses and extract relevant details
        for item in data:
            # Collect data from each item and append to the response list
            Event_ID = str(item.get("Event_ID"))
            Source = str(item.get("Source"))
            Event_Name = str(item.get("Event_Name"))
            for i in batch_responses:  # Assuming batch_responses is a list of response objects
                custom_id = i.custom_id
                if Event_ID in custom_id:
                    message_content = get_message_by_custom_id(batch_responses, custom_id)
                    # Create a dictionary with the extracted information
                    df = {"Event_ID": Event_ID, "Sources": Source, "Event_Names": Event_Name}
                    df.update(message_content)

            # Append the dictionary to the response list
            response.append(df)

    out_file_path = f"{args.output_dir}/{args.filename.replace('.json', '')}_rawoutput.json"
    with open(out_file_path, "w") as json_file:
        json.dump(response, json_file, indent=4)
