import argparse
import json
import os
import pathlib
from pathlib import Path
import openai
from dotenv import load_dotenv
from Database.Prompts.prompts import check_Event, checking_event_V2
from Database.scr.log_utils import Logging
import argparse
import json
import os
import pathlib
from pathlib import Path
import pandas as pd

from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI

import openai
from dotenv import load_dotenv
from pydantic import BaseModel, create_model
from typing import List


def gpt_checking(res_format, user_input, sys_prompt, client):
    try:
        response = client.chat.completions.create(
            response_format=res_format,
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "developer", "content": sys_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0,
            max_tokens=4096,
            n=1,
            stop=None
        )
        message = response.choices[0].message.content
       # Try to parse message as JSON
        try:
            parsed_response = json.loads(message)
            return parsed_response
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response")
            return {}

    except Exception as e:
            logger.error(f"Failed to get a response: {e}")
            return {}
if __name__ == "__main__":
    logger = Logging.get_logger("run filtering")

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", dest="filename", help="The name of the json file in the <Wikipedia articles> directory", type=str)
    parser.add_argument("-r", "--raw_dir", dest="raw_dir", help="The directory containing Wikipedia json files to be run", type=str)
    parser.add_argument("-e", "--api_env", dest="api_env", help="The env file that contains the API keys.", type=str)
    parser.add_argument("-o", "--output_dir", dest="output_dir", help="The output directory for processed files.", type=str)

    args = parser.parse_args()
    logger.info(f"Passed args: {args}")
    logger.info(f"Creating {args.output_dir} if it does not exist!")

    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    # Set up the environment
    env_path = Path(args.api_env)
    load_dotenv(dotenv_path=env_path)
    client = openai.OpenAI(api_key=os.getenv("API_KEY"))

    try:
        with open(f"{args.raw_dir}/{args.filename}", "r") as file:
            raw_text = json.load(file)
    except Exception as e:
        logger.error(f"Failed to load file: {e}")
  

    raw_text_new = []
    
    for item in raw_text:
        event = {key: item.get(key) for key in ["Source", "Whole_Text", "Event_ID", "Info_Box", "Article_Name"]}

        all_tables_new = []
        list_new = []
        re_note= []

        for i in item.get("All_Tables", []):
            for table in i:
                user_input = f"Content: {str(table)}"
                sys_prompt = checking_event_V2
                res_format = check_Event()
                RE = gpt_checking(res_format, user_input, sys_prompt, client)
                if "Yes" in RE.get("Checking_response"):
                    all_tables_new.append(i)
                    i_re=f"{user_input}+{RE}"
                    re_note.append(i_re)
        for i in item.get("Lists", []):
            user_input = f"Content: {str(i)}"
            res_format = check_Event()
            RE = gpt_checking(res_format, user_input, sys_prompt, client)
           
            if "Yes" in RE.get("Checking_response"):
                list_new.append(i)
                i_re=f"{user_input}+{RE}"
                re_note.append(i_re)
        event["All_Tables"] = all_tables_new
        event["Lists"] = list_new
        event["re_note"]=re_note

        raw_text_new.append(event)

    try:
        output_path = f"{args.output_dir}/{args.filename}"
        with open(output_path, "w") as json_file:
            json.dump(raw_text_new, json_file, indent=4)
        logger.info(f"Output written to {output_path}")
    except Exception as e:
        logger.error(f"Failed to write output file: {e}")


    