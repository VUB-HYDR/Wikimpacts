import argparse
import json
import os
import pathlib
from pathlib import Path

import openai
from dotenv import load_dotenv

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
    parser.add_argument(
        "-p",
        "--prompt_list",
        dest="prompt_list",
        default="V_3",
        help="The list of prompts for information extraction, choosing from V_0 to V_X",
        type=dict,
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
    def batch_gpt_basic(prompt, event_id):
        df = {
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
    def batch_gpt_impact(prompt, event_id):
        df = {
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

        # generate the batch file
        for key, value in args.prompt_list:
            if key in prompt_basic_list:
                batch_gpt_impact()
