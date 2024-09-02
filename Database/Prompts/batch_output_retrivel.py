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
        dest="filename",
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
    file_path = f"{args.raw_dir}/{args.filename}"
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
                    message = message.replace("```json", "").replace("```", "").strip('"').strip()
                    try:
                        return json.loads(message)
                    except:
                        try:
                            ## an ugly hack for a persistent json error
                            message = message.replace("\n}\n\n\n{", ",")
                            return json.loads(message)
                        except:
                            return {"Json_Error": message}
                except (KeyError, IndexError) as e:
                    return f"Error retrieving message: {str(e)}"
        return f"No response found for custom_id: {custom_id}"

    # Initialize an empty list to store the results
    response = []

    # Retrieve the list of batches
    batches = client.batches.list()
    # Iterate over the provided data
    for item in data:
        # Extract relevant details from each item in the data
        Event_ID = str(item.get("Event_ID"))
        Source = str(item.get("Source"))
        Event_Name = str(item.get("Event_Name"))

        # Initialize the base dictionary for each event
        df = {"Event_ID": Event_ID, "Sources": Source, "Event_Names": Event_Name}
        # Iterate over each batch
        for batch in batches:
            batch_id = batch.id
            output_file_id = batch.output_file_id
            # Retrieve the batch details (if needed)
            client.batches.retrieve(batch_id)
            # Retrieve the file content associated with the output_file_id
            file_response = client.files.content(output_file_id)
            batch_responses = file_response.text
            # Iterate over the parsed JSON lines and find all matching custom_ids
            res = [json.loads(line) for line in batch_responses.strip().splitlines()]
            for i in res:
                custom_id = i.get("custom_id", "")
                if Event_ID in custom_id:
                    try:
                        # Retrieve the message content for the matching custom_id
                        message_content = get_message_by_custom_id(res, custom_id)

                        # Update the df dictionary with the message content directly
                        df.update(message_content)
                    except json.JSONDecodeError as e:
                        # If a JSONDecodeError occurs, log the error in the df
                        df["Json_Error"] = str(e)
                # Append the dictionary to the response list
        response.append(df)

    out_file_path = f"{args.output_dir}/{args.filename.replace('.json', '')}_rawoutput.json"
    with open(out_file_path, "w") as json_file:
        json.dump(response, json_file, indent=4)
