# checking the status of batch and retrive the results
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
        help="The directory where the LLM outputs will land (as .json)",
        type=str,
    )
    parser.add_argument(
        "-f",
        "--batch_filename",
        dest="batch_filename",
        help="The name of the jsonl file in the batch folder",
        type=str,
    )
    parser.add_argument(
        "-b",
        "--batch_dir",
        dest="batch_dir",
        help="The directory where the batch file lands (as .jsonl)",
        type=str,
    )
    args = parser.parse_args()
    logger.info(f"Passed args: {args}")
    logger.info(f"Loading {args.batch_dir}")
    pathlib.Path(args.batch_dir).mkdir(parents=True, exist_ok=True)
    file_path = f"{args.batch_dir}/{args.filename}"
    with open(file_path, "r") as file:
        # Process each line in the file
        for line in file:
            # Parse the JSON object from the line
            data = json.loads(line)
    """
    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    """

    env_path = Path(args.api_env)
    load_dotenv(dotenv_path=env_path)
    client = openai.OpenAI(api_key=os.getenv("API_KEY"))
    # return the batches information, and access the ids, only when the task is completed
    # the custom id with the prompt category, and append them together
    # metadata={'description': 'batch job for basic information'}

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
        batch_responses = file_response.json()

        # Iterate over the batch responses and extract relevant details
        for item in batch_responses:  # Assuming batch_responses is a list of response objects
            custom_id = item.get("custom_id")
            message_content = get_message_by_custom_id(batch_responses, custom_id)

            # Collect data from each item and append to the response list
            Event_ID = str(item.get("Event_ID", "N/A"))  # Replace with actual key if different
            Source = str(item.get("Source", "N/A"))  # Replace with actual key if different
            Event_Name = str(item.get("Event_Name", "N/A"))  # Replace with actual key if different

            # Create a dictionary with the extracted information
            df = {"Event_ID": Event_ID, "Source": Source, "Event_Name": Event_Name, "Message_Content": message_content}

            # Append the dictionary to the response list
            response.append(df)
