import argparse
import json
import os
import pathlib
from pathlib import Path

import openai
from dotenv import load_dotenv

from Database.Prompts.prompts import V_3_2 as target_prompts
from Database.scr.log_utils import Logging

# the prompt list need to use the same variable names in our schema, and each key contains 1+ prompts
if __name__ == "__main__":
    logger = Logging.get_logger("run prompts")

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        help="The name of the json file in the <Wikipedia articles> directory",
        type=str,
    )

    parser.add_argument(
        "-r",
        "--raw_dir",
        dest="raw_dir",
        help="The directory containing Wikipedia json files to be run",
        type=str,
    )

    parser.add_argument(
        "-b",
        "--batch_dir",
        dest="batch_dir",
        help="The directory where the batch file will land (as .jsonl)",
        type=str,
    )
    parser.add_argument(
        "-m",
        "--model_name",
        dest="model_name",
        default="gpt-4o-2024-05-13",  # This model supports at most 4096 completion tokens, and need to specify json-output
        help="The model version applied in the experiment, like gpt-4o-mini. ",
        type=str,
    )
    parser.add_argument(
        "-t",
        "--max_tokens",
        dest="max_tokens",
        default=4096,  # This default model supports at most 4096 completion tokens
        help="The max tokens of the model selected",
        type=int,
    )

    parser.add_argument(
        "-e",
        "--api_env",
        dest="api_env",
        help="The env file that contains the API keys.",
        type=str,
    )

    parser.add_argument(
        "-d",
        "--description",
        dest="description",
        help="The description of the experiment",
        type=str,
    )

    parser.add_argument(
        "-p",
        "--prompt_category",
        dest="prompt_category",
        help="The prompt category of the experiment, can only choose from impact, basic, and all",
        type=str,
    )
    args = parser.parse_args()
    logger.info(f"Passed args: {args}")

    logger.info(f"Creating {args.batch_dir} if it does not exist!")

    pathlib.Path(args.batch_dir).mkdir(parents=True, exist_ok=True)
    # load openai models
    # Explicitly set the path to the .env file
    env_path = Path(args.api_env)
    load_dotenv(dotenv_path=env_path)
    client = openai.OpenAI(api_key=os.getenv("API_KEY"))

    # input the raw articles for processing
    with open(f"{args.raw_dir}/{args.filename}", "r") as file:
        # Step 2: Load the JSON data into a Python dictionary
        raw_text = json.load(file)

    # define the gpt setting for "gpt-4o-2024-05-13", because the setting in the "gpt-4o-2024-08-06" is different, we divide two functions to run them
    def batch_gpt_basic(prompt, event_id):
        df = {
            "custom_id": event_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "response_format": {"type": "json_object"},
                "model": args.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a climate scientist. You will be provided with an article to analyze the basic information of a disaster event. Please take your time to read the text thoroughly and conduct the analysis step by step.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,  # randomness
                "max_tokens": args.max_tokens,
                "n": 1,
                "top_p": 1,  # default
                "stop": None,
            },
        }
        return df

    # the system role is differ from the basic
    def batch_gpt_impact(prompt, event_id):
        df = {
            "custom_id": event_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "response_format": {"type": "json_object"},
                "model": args.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a climate impact analyst. You will be provided with an article to analyze the detailed impact of a disaster event. Please take your time to read the text thoroughly and conduct the analysis step by step.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,  # randomness
                "max_tokens": args.max_tokens,
                "n": 1,
                "top_p": 1,  # default
                "stop": None,
            },
        }
        return df

    # Function to process the raw article
    def process_whole_text(data):
        filtered_data = [item for item in data["Whole_Text"] if item["content"] not in [None, ""]]
        result = " ".join([f"header: {item['header']}, content: {item['content']}" for item in filtered_data])
        return result

    # list of keys for prompt of basic and impact information
    prompt_basic_list = ["location_time", "main_event_hazard"]
    prompt_impact_list = [
        "deaths",
        "homeless",
        "injuries",
        "buildings_damaged",
        "displaced",
        "affected",
        "damage",
        "insured_damage",
    ]

    # Define the file path for the JSONL file
    jsonl_file_path_basic = (
        f"{args.batch_dir}/{args.filename.replace('.json', '')}_{args.description}_{args.model_name}_basic.jsonl"
    )
    jsonl_file_path_impact = (
        f"{args.batch_dir}/{args.filename.replace('.json', '')}_{args.description}_{args.model_name}_impact.jsonl"
    )

    def generate_batch_data(raw_text, target_prompts, prompt_basic_list, prompt_impact_list):
        """
        Generates basic and impact batch data using target prompts for each category.

        Parameters:
        - raw_text: list of events containing 'Event_ID', 'Event_Name', 'Info_Box', etc.
        - target_prompts: dictionary where keys are categories (e.g., 'deaths', 'injuries') and values are lists of prompts
        - prompt_basic_list: list of categories that should be processed for basic data
        - prompt_impact_list: list of categories that should be processed for impact data

        Returns:
        - basic_data: list of formatted batch lines for basic data processing
        - impact_data: list of formatted batch lines for impact data processing
        """
        basic_data = []
        impact_data = []

        # Process basic data
        basic_data = process_data(raw_text, target_prompts, prompt_basic_list, batch_gpt_basic)

        # Process impact data
        impact_data = process_data(raw_text, target_prompts, prompt_impact_list, batch_gpt_impact)

        return basic_data, impact_data

    def process_data(raw_text, target_prompts, prompt_list, batch_function):
        """
        Processes data based on a prompt list and batch function.

        Parameters:
        - raw_text: list of events containing 'Event_ID', 'Event_Name', 'Info_Box', etc.
        - target_prompts: dictionary where keys are categories (e.g., 'deaths', 'injuries') and values are lists of prompts
        - prompt_list: list of categories to be processed
        - batch_function: function to call for generating the batch line (either batch_gpt_basic or batch_gpt_impact)

        Returns:
        - data: list of formatted batch lines
        """
        data = []
        for key, prompt_list_for_key in target_prompts.items():
            if key in prompt_list:
                for item in raw_text:
                    event_id_base = str(item.get("Event_ID"))
                    event_name = str(item.get("Event_Name"))
                    info_box = str(item.get("Info_Box"))
                    whole_text = process_whole_text(item)

                    # Iterate over each prompt in the list and format them
                    for idx, prompt_template in enumerate(prompt_list_for_key, start=1):
                        event_id = f"{event_id_base}_{key}_{idx}"  # unique event id with key and index
                        prompt = prompt_template.format(Info_Box=info_box, Whole_Text=whole_text, Event_Name=event_name)

                        line = batch_function(prompt, event_id)  # define the line of API request
                        data.append(line)

        return data

    def save_batch_file(data, file_path, description):
        """
        Save the batch data to a .jsonl file.

        Parameters:
        - data: List of batch data entries to be saved
        - file_path: Path where the .jsonl file should be saved
        - description: Description for logging purposes (basic or impact)
        """
        logger.info(f"Saving the batch file for {description} information")
        with open(file_path, "w") as jsonl_file:
            for entry in data:
                jsonl_file.write(json.dumps(entry) + "\n")

    def upload_batch_file(file_path, description, client, metadata_description):
        """
        Upload a batch file to OpenAI and create a batch job.

        Parameters:
        - file_path: Path of the .jsonl file to upload
        - description: Description for logging purposes (basic or impact)
        - client: OpenAI API client
        - metadata_description: Description for the batch metadata
        """
        logger.info(f"Uploading the batch file for {description} information")

        # Upload the batch file to OpenAI
        with open(file_path, "rb") as file_to_upload:
            batch_input_file = client.files.create(file=file_to_upload, purpose="batch")

        # Retrieve the file ID
        batch_input_file_id = batch_input_file.id

        # Create the batch job
        client.batches.create(
            input_file_id=batch_input_file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"description": metadata_description},
        )

    # Helper function to process, save, and upload batch data
    def process_save_upload(data, jsonl_file_path, description, client, metadata_description):
        # Save the batch data to a JSONL file
        save_batch_file(data, jsonl_file_path, description)
        # Upload the batch file to OpenAI
        upload_batch_file(
            file_path=jsonl_file_path,  # path to the batch file
            description=description,  # description for logging
            client=client,  # OpenAI API client instance
            metadata_description=metadata_description,  # metadata description
        )

    if args.prompt_category == "impact":
        # Process data for impact
        impact_data = process_data(raw_text, target_prompts, prompt_impact_list, batch_gpt_impact)
        process_save_upload(
            impact_data,
            jsonl_file_path_impact,
            args.description,
            client,
            f"{args.description}_{args.model_name}_{args.filename}",
        )

    elif args.prompt_category == "basic":
        # Process data for basic
        basic_data = process_data(raw_text, target_prompts, prompt_basic_list, batch_gpt_basic)
        process_save_upload(
            basic_data,
            jsonl_file_path_basic,
            args.description,
            client,
            f"{args.description}_{args.model_name}_{args.filename}",
        )

    elif args.prompt_category == "all":
        # Process and upload basic data
        basic_data = process_data(raw_text, target_prompts, prompt_basic_list, batch_gpt_basic)
        process_save_upload(
            basic_data,
            jsonl_file_path_basic,
            args.description,
            client,
            f"{args.description}_{args.model_name}_{args.filename}",
        )

        # Process and upload impact data
        impact_data = process_data(raw_text, target_prompts, prompt_impact_list, batch_gpt_impact)
        process_save_upload(
            impact_data,
            jsonl_file_path_impact,
            args.description,
            client,
            f"{args.description}_{args.model_name}_{args.filename}",
        )
