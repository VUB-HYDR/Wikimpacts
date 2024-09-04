import argparse
import json
import os
import pathlib
from pathlib import Path

import openai
from dotenv import load_dotenv

# the newest version of prompts are applied
from Database.Prompts.prompts import V_3
from Database.scr.normalize_utils import Logging

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
        "-e",
        "--api_env",
        dest="api_env",
        help="The env file that contains the API keys.",
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

    # define the gpt setting
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
                "max_tokens": 4096,
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
                "max_tokens": 4096,
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
        "insured_Damage",
    ]

    # Define the file path for the JSONL file
    jsonl_file_path_basic = f"{args.batch_dir}/{args.filename.replace('.json', '')}_basic.jsonl"
    jsonl_file_path_impact = f"{args.batch_dir}/{args.filename.replace('.json', '')}_impact.jsonl"

    # generate the batch file
    basic_data = []
    impact_data = []
    for key, value in V_3.items():
        if key in prompt_basic_list:
            for item in raw_text:
                event_id = (
                    str(item.get("Event_ID")) + "_" + str(key)
                )  # each event id will append with the prompt category, like deaths, injuries, etc to retrive in the output, and make the id unique
                event_name = str(item.get("Event_Name"))
                info_box = str(item.get("Info_Box"))
                wholt_text = process_whole_text(item)
                prompt = V_3[key].format(Info_Box=info_box, Whole_Text=wholt_text, Event_Name=event_name)
                line = batch_gpt_basic(prompt, event_id)  # define the line of api request
                basic_data.append(line)
        if key in prompt_impact_list:
            for item in raw_text:
                event_id = (
                    str(item.get("Event_ID")) + "_" + str(key)
                )  # each event id will append with the prompt category, like deaths, injuries, etc to retrive in the output, and make the id unique
                event_name = str(item.get("Event_Name"))
                info_box = str(item.get("Info_Box"))
                wholt_text = process_whole_text(item)
                prompt = V_3[key].format(Info_Box=info_box, Whole_Text=wholt_text, Event_Name=event_name)
                line = batch_gpt_impact(prompt, event_id)  # define the line of api request
                impact_data.append(line)
    logger.info(f"Saving the batch file for basic information")
    with open(jsonl_file_path_basic, "w") as jsonl_file:
        for entry in basic_data:
            jsonl_file.write(json.dumps(entry) + "\n")
    logger.info(f"Saving the batch file for impact information")
    with open(jsonl_file_path_impact, "w") as jsonl_file:
        for entry in impact_data:
            jsonl_file.write(json.dumps(entry) + "\n")

    # upload the batch file to openai
    # basic information
    logger.info(f"Uploaoding the batch file for basic information")
    batch_input_file_basic = client.files.create(file=open(jsonl_file_path_basic, "rb"), purpose="batch")
    batch_input_file_basic_id = batch_input_file_basic.id

    client.batches.create(
        input_file_id=batch_input_file_basic_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": f"batch job for basic information of file {args.filename}"},
    )

    # impact information
    logger.info(f"Uploading the batch file for impact information")
    batch_input_file_impact = client.files.create(file=open(jsonl_file_path_impact, "rb"), purpose="batch")
    batch_input_file_impact_id = batch_input_file_impact.id

    client.batches.create(
        input_file_id=batch_input_file_impact_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": f"batch job for impact information of file {args.filename}"},
    )
