import argparse
import json
import os
import pathlib
from pathlib import Path

import openai
from dotenv import load_dotenv
from prompts import V_3  # change here to choose the version of prompts

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
        "-o",
        "--output_dir",
        dest="output_dir",
        help="The directory where the LLM outputs will land (as .json)",
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
        default="gpt-4o-2024-05-13",  # This model supports at most 4096 completion tokens
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

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # load openai models
    # Explicitly set the path to the .env file
    env_path = Path(args.api_env)
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("API_KEY")
    openai.api_key = api_key
    # API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
    # input the raw articles for processing
    with open(f"{args.raw_dir}/{args.filename}", "r") as file:
        # Step 2: Load the JSON data into a Python dictionary
        raw_text = json.load(file)

    # notice that due to the different version of prompts applied, the keys may a bit different, below is the version V_3
    # list of keys for prompt of basic and impact information
    prompt_basic_list = ["location_time", "main_event_hazard"]
    prompt_impact_list = [
        "Deaths",
        "Homeless",
        "Injuries",
        "Buildings_Damaged",
        "Displaced",
        "Affected",
        "Damage",
        "Insured_Damage",
    ]

    # define the gpt setting
    def batch_gpt_basic(prompt, event_id, category):
        df = {
            "Category": category,  # define the experiment category, like deaths, injuries etc
            "custom_id": event_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
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
    def batch_gpt_impact(prompt, event_id, category):
        df = {
            "Category": category,  # define the experiment category, like deaths, injuries etc
            "custom_id": event_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
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

    # generate the batch file
    basic_data = []
    impact_data = []
    for key, value in V_3:
        if key in prompt_basic_list:
            for item in raw_text:
                event_id = str(item.get("Event_ID"))
                event_name = str(item.get("Event_Name"))
                info_box = str(item.get("Info_Box"))
                wholt_text = process_whole_text(item)
                prompt = V_3[key].format(Info_Box=info_box, Whole_Text=wholt_text, Event_Name=event_name)
                line = batch_gpt_basic(prompt, event_id, key)  # define the line of api request
                basic_data.append(line)
        if key in prompt_impact_list:
            for item in raw_text:
                event_id = str(item.get("Event_ID"))
                event_name = str(item.get("Event_Name"))
                info_box = str(item.get("Info_Box"))
                wholt_text = process_whole_text(item)
                prompt = V_3[key].format(Info_Box=info_box, Whole_Text=wholt_text, Event_Name=event_name)
                line = batch_gpt_impact(prompt, event_id, key)  # define the line of api request
                impact_data.append(line)

    with open(f"{args.batch_dir}/{args.filename.replace('.json', '')}_basic.jsonl", "w") as jsonl_file:
        for entry in basic_data:
            jsonl_file.write(json.dumps(entry) + "\n")
    with open(f"{args.batch_dir}/{args.filename.replace('.json', '')}_impact.jsonl", "w") as jsonl_file:
        for entry in impact_data:
            jsonl_file.write(json.dumps(entry) + "\n")
