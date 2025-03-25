import os
import sys
from fastapi import FastAPI

import openai
from dotenv import load_dotenv
from typing import List
from fastapi.encoders import jsonable_encoder
import json 
import pathlib
from pathlib import Path
import pandas as pd 
from Database.Prompts.prompts import generate_translation
from Database.scr.log_utils import Logging
import argparse
# the prompt list need to use the same variable names in our schema, and each key contains 1+ prompts
if __name__ == "__main__":
    import logging
    logger = logging.getLogger("run prompts")

    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        help="The name of the json file in the <Wikidata articles> directory",
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
        help="The directory for the output file",
        type=str,
    )

 
    parser.add_argument(
        "-e",
        "--env",
        dest="api_env",
        help="The path to the .env file containing API keys",
        type=str,
    )
    args = parser.parse_args()
    logger.info(f"Passed args: {args}")

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    def gpt_completion(res_format, user_input):
        response = client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        messages=[
            {
                "role": "developer",
                "content": "Translate the following text (in a detected language) into English."
            },
            {
                "role": "user",
                "content": f"Provide only the translated output without any additional text, explanations, or formatting. {user_input}"
            }
        ],
        temperature=0,  # randomness
        max_tokens=16384,
        n=1,
        stop=None
    )
        message =  response.choices[0].message.content
        return message
    

    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    env_path = Path(args.api_env)
    load_dotenv(dotenv_path=env_path)
    client = openai.OpenAI(api_key=os.getenv("API_KEY"))
    with open(f"{args.raw_dir}/{args.filename}", "r") as file:
            # Step 2: Load the JSON data into a Python dictionary
            df = json.load(file)
    def translate_whole_text(whole_text):
        translated_texts = []
        for item in whole_text:
            translated_header = None if not item['header'] or item['header'].strip() == '' else gpt_completion(generate_translation, f"Text: {item['header']}")
            translated_content = None if not item['content'] or item['content'].strip() == '' else gpt_completion(generate_translation, f"Text: {item['content']}")
            translated_texts.append({
                'header': translated_header,
                'content': translated_content
            })
        return translated_texts
   
    def translate_all_tables(all_tables):
        translated_tables = []
        for table in all_tables:
            translated_table = []
            for entry in table:
                translated_entry = {
                    key if key is None or key.strip() == '' else gpt_completion(generate_translation, key): 
                    value if value is None or value.strip() == '' else gpt_completion(generate_translation, value)
                    for key, value in entry.items()
                }
                translated_table.append(translated_entry)
            translated_tables.append(translated_table)
        return translated_tables



    def translate_infobox(info_box):
        translated_infobox = None if not info_box or info_box.strip() == '' else gpt_completion(generate_translation, f"Text: {info_box}")
        return translated_infobox

    translated_df = []
    for item in df[100:200]:
        translated_event = {}
        event_id = item["Event_ID"]
        source = item["Source"]
        article_name = item["Article_Name"]
        whole_text = item["Whole_Text"]
        info_box = item["Info_Box"]
        all_tables = item["All_Tables"]
        
        translated_text = translate_whole_text(whole_text)
        translated_tables = translate_all_tables(all_tables)
        translated_infobox = translate_infobox(info_box)
        
        translated_event = {
            "Event_ID": event_id,
            "Source": source,
            "Article_Name": article_name,
            "Whole_Text": translated_text,
            "Info_Box": translated_infobox,
            "All_Tables": translated_tables
        }
        
        translated_df.append(translated_event)

    with open(f"{args.output_dir}/{args.filename}", "w") as file:
        # Convert the list of dictionaries to JSON and write to file
        json.dump(translated_df, file, ensure_ascii=False, indent=4)
