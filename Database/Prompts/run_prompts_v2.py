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
from Database.Prompts.prompts import V_7_1 as target_prompts
from Database.Prompts.prompts import  V_7_1_m, generate_MultiEvent, generate_LocationEvent, Post_location, generate_total_direct_schema, generate_total_monetary_schema, generate_TotalMainEvent, generate_TotalLocationEvent
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
        default="o3-mini-2025-01-31",  # This model supports at most 4096 completion tokens, and need to specify json-output
        help="The model version applied in the experiment, like gpt-4o-mini. ",
        type=str,
    )
    parser.add_argument(
        "-t",
        "--max_tokens",
        dest="max_tokens",
        default=100000,  # This default model supports more completion tokens than GPT4o model 
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
        help="The prompt category of the experiment, can only choose from impact, basic, all and location_chain",
        type=str,
    )

    parser.add_argument(
        "-a",
        "--article_category",
        dest="article_category",
        help="The article category of the experiment, can only choose from single and multi",
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
    
    with open(f"{args.raw_dir}/{args.filename}", "r") as file:
        # Step 2: Load the JSON data into a Python dictionary
        raw_text = json.load(file)
   

    # define the gpt setting for "gpt-4o-2024-05-13", because the setting in the "gpt-4o-2024-08-06" is different, we divide two functions to run them
    def batch_gpt(prompt, event_id,user_input,re_format):
        df = {
            "custom_id": event_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "response_format": re_format,
                "model": args.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {"role": "user", "content": user_input},
                ],
                "reasoning_effort":"high",
                "max_completion_tokens": args.max_tokens,
              
                "stop": None,
            },
        }
        return df
    
    # for location chain completion 
    def gpt_completion(res_format, user_input, sys_prompt):
         response = client.chat.completions.create(
        # gpt4-mini-model 
        
                response_format=res_format,
                model="gpt-4o-mini-2024-07-18",
                    messages=[

            {
            "role": "developer",
            "content": sys_prompt
        },
        
                { "role": "user",
                    "content": user_input}
                
            ],
            
                temperature=0,# randomness
                max_tokens=4096,
                n=1,
                stop=None
            )
         message = response.choices[0].message.content
         return message
     
   
    def update_location_chains_for_specific_columns(df):
        """
        Updates all columns starting with 'Specific' in the DataFrame with location chains.
        """
        # Iterate through all columns in the DataFrame
        for column_name in df.columns:
            # Check if column name starts with 'Specific'
            if column_name.startswith("Specific"):
                # Iterate through each row in the column
                for index, row in df.iterrows():
                    specific_list = row[column_name]
                    if isinstance(specific_list, list):
                        # Iterate through each dictionary in the list
                        for item in specific_list:
                            country = item['Administrative_Area']
                            locations = item['Locations']
                            user_input= f"Country: {country}, a list of locations: {locations}."
                            res_format= generate_LocationEvent()
                            location_chain = gpt_completion(res_format,user_input, Post_location )
                            item['Location_Chain'] = location_chain
        return df

# user input information box {Info_Box} and header-content pair article {Whole_Text}
# output Specific_Instance_Per_Administrative_Area_// Total_Summary_
    # Function to process the raw single event article
    def process_whole_text(data):
        filtered_data = [item for item in data["Whole_Text"] if item["content"] not in [None, ""]]
        result = " ".join([f"header: {item['header']}, content: {item['content']}" for item in filtered_data])
        return result
  
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

    # Define the file path for the JSONL file
    jsonl_file_path_basic = (
        f"{args.batch_dir}/{args.filename.replace('.json', '')}_{args.description}_{args.model_name}_basic.jsonl"
    )
    jsonl_file_path_impact = (
        f"{args.batch_dir}/{args.filename.replace('.json', '')}_{args.description}_{args.model_name}_impact.jsonl"
    )

  
    # single event 
    def process_single_data(raw_text, target_prompts, prompt_list):
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
                

                    if "Damage" in key and "Building" not in key:
                        # Iterate over each prompt in the list and format them
                        for idx, prompt_template in enumerate(prompt_list_for_key, start=1):
                            
                            event_id = f"{event_id_base}_{key}_{idx}"  # unique event id with key and index
                            sys_prompt = prompt_template.format(Event_Name=event_name)
                            user_input=f"information box {info_box} and header-content pair article {whole_text}"
                            re_format_obj = generate_total_monetary_schema(key)  
                            line = batch_gpt(sys_prompt, event_id,user_input,re_format_obj)  # define the line of API request
                            data.append(line)
                    elif "main" in key:
                            for idx, prompt_template in enumerate(prompt_list_for_key, start=1):
                                    
                                    event_id = f"{event_id_base}_{key}_{idx}"  # unique event id with key and index
                                    sys_prompt = prompt_template.format(Event_Name=event_name)
                                    user_input=f"information box {info_box} and header-content pair article {whole_text}"
                              
                                  
                                    TotalMainEvent=generate_TotalMainEvent()
                                    line = batch_gpt(sys_prompt, event_id,user_input,TotalMainEvent)  # define the line of API request
                                    data.append(line)
                    elif "location" in key:
                      for idx, prompt_template in enumerate(prompt_list_for_key, start=1):
                                    
                                    event_id = f"{event_id_base}_{key}_{idx}"  # unique event id with key and index
                                    sys_prompt = prompt_template.format(Event_Name=event_name)
                                    user_input=f"information box {info_box} and header-content pair article {whole_text}"
                                    TotalLocationEvent=generate_TotalLocationEvent()
                                    line = batch_gpt(sys_prompt, event_id,user_input,TotalLocationEvent)  # define the line of API request
                                    data.append(line)
                    else:
                        for idx, prompt_template in enumerate(prompt_list_for_key, start=1):
                            
                            event_id = f"{event_id_base}_{key}_{idx}"  # unique event id with key and index
                            sys_prompt = prompt_template.format(Event_Name=event_name)
                            user_input=f"information box {info_box} and header-content pair article {whole_text}"
                            re_format_obj= generate_total_direct_schema(key)
                            line = batch_gpt(sys_prompt, event_id,user_input,re_format_obj)  # define the line of API request
                            data.append(line)

        return data

     # multi event 
    """
    def process_multi_data(raw_text, target_prompts):
      
        Processes data based on a prompt list and batch function.

        Parameters:
        - raw_text: list of events containing 'Event_ID', 'Event_Name', 'Info_Box', etc.
        - target_prompts: dictionary where keys are categories (e.g., 'deaths', 'injuries') and values are lists of prompts

        Returns:
        - data: list of formatted batch lines
     
        data = []
  
                
        for item in raw_text:
            
            event_id_base = str(item.get("Event_ID"))
            
            info_box = str(item.get("Info_Box"))
            whole_text = item.get("Whole_Text")
            All_tables= item.get("All_Tables")
            Lists=item.get("Lists")
            if whole_text: 
                for idx, i in enumerate(whole_text):
                    # Defensive: Ensure i is dict before calling .get
                    if not isinstance(i, dict):
                        continue  # or handle error
                    event_name = str(i.get("header") or i.get("Header"))
                    content    = str(i.get("content") or i.get("Content"))
                    if content is not None and content.strip() != '': 
                        event_id = f"{event_id_base}_{idx}"  # unique id with key and index
                        sys_prompt = target_prompts.format(Event_Name=event_name if event_name else "event")
                        user_input=f" Content: {content}"
                        re_format_obj = generate_MultiEvent()  
                        line = batch_gpt(sys_prompt, event_id, user_input, re_format_obj)  # define the line of API request
                        data.append(line)
            #  for tables, the event_name is not easy to obtain directly, therefore, just use "event"
            if All_tables:  # Checks All_tables is not None and not empty list
                for table in All_tables:
                    # Assuming 'table' is an iterable of rows or items you want to process
                    for idx, i in enumerate(table):
                        # Defensive: Ensure 'i' is a string before applying strip()
                        if isinstance(i, str) and i.strip() != '': 
                            event_id = f"{event_id_base}_{idx}"  # unique event id with key and index
                            sys_prompt = target_prompts.format(Event_Name="event")
                            user_input = f" Content: {i}"
                            re_format_obj = generate_MultiEvent()  
                            line = batch_gpt(sys_prompt, event_id, user_input, re_format_obj)
                            data.append(line)
            if Lists is not None and Lists.strip() != '': 
            
                    for idx, i in Lists:
                        if i is not None and i.strip() != '': 
                            event_id = f"{event_id_base}_{idx}"  # unique event id with key and index
                            sys_prompt = target_prompts.format(Event_Name="event")
                            user_input=f" Content: {i}"
                            re_format_obj = generate_MultiEvent()  
                            line = batch_gpt(sys_prompt, event_id,user_input,re_format_obj)  # define the line of API request
                            data.append(line)
                        
                               
                   
        return data
    """
    def process_multi_data(raw_text, target_prompts):
        """
        Processes data based on a prompt list and batch function.

        Parameters:
        - raw_text: list of events containing 'Event_ID', 'Event_Name', 'Info_Box', etc.
        - target_prompts: dictionary where keys are categories (e.g., 'deaths', 'injuries') and values are lists of prompts

        Returns:
        - data: list of formatted batch lines
        """
        data = []
        for item in raw_text:
            event_id_base = str(item.get("Event_ID"))
            
            info_box = str(item.get("Info_Box"))
            whole_text = item.get("Whole_Text")
            All_tables = item.get("All_Tables")
            Lists = item.get("Lists")
            
            # --- Use a single counter for this item ---
            idx = 0
            
            # Process whole_text
            if whole_text:
                for i in whole_text:
                    if not isinstance(i, dict):
                        continue
                    event_name = str(i.get("header") or i.get("Header"))
                    content    = str(i.get("content") or i.get("Content"))
                    if content is not None and content.strip() != '':
                        event_id = f"{event_id_base}_{idx}"
                        sys_prompt = target_prompts.format(Event_Name=event_name if event_name else "event")
                        user_input = f" Content: {content}"
                        re_format_obj = generate_MultiEvent()
                        line = batch_gpt(sys_prompt, event_id, user_input, re_format_obj)
                        data.append(line)
                        idx += 1  # increment main index
            
            # Process All_tables
            if All_tables:
                for table in All_tables:
                    for i in table:
                        if isinstance(i, str) and i.strip() != '':
                            event_id = f"{event_id_base}_{idx}"
                            sys_prompt = target_prompts.format(Event_Name="event")
                            user_input = f" Content: {i}"
                            re_format_obj = generate_MultiEvent()
                            line = batch_gpt(sys_prompt, event_id, user_input, re_format_obj)
                            data.append(line)
                            idx += 1

            # Process Lists
            if Lists:
                # If Lists is a string (should be list ideally)
                if isinstance(Lists, str):
                    Lists = [Lists]
                for i in Lists:
                    if isinstance(i, str) and i.strip() != '':
                        event_id = f"{event_id_base}_{idx}"
                        sys_prompt = target_prompts.format(Event_Name="event")
                        user_input = f" Content: {i}"
                        re_format_obj = generate_MultiEvent()
                        line = batch_gpt(sys_prompt, event_id, user_input, re_format_obj)
                        data.append(line)
                        idx += 1

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
   

    if args.prompt_category == "location_chain":
    # Convert the JSON data into a DataFrame
        df = pd.DataFrame(raw_text)

        # Apply the function to update specific columns in the DataFrame
        Processed_df = update_location_chains_for_specific_columns(df)

        json_output_path = f"{args.raw_dir}/{args.filename.replace('.json', '_location_processed.json')}"

        df.to_json(json_output_path, orient='records', indent=2)
    elif args.prompt_category == "impact" and args.article_category == "single":
        # Process data for impact
        impact_data = process_single_data(raw_text, target_prompts, prompt_impact_list)
        process_save_upload(
            impact_data,
            jsonl_file_path_impact,
            args.description,
            client,
            f"{args.description}_{args.model_name}_{args.filename}",
        )

    elif args.prompt_category == "basic"and args.article_category == "single":
        # Process data for basic
        basic_data = process_single_data(raw_text, target_prompts, prompt_basic_list)
        process_save_upload(
            basic_data,
            jsonl_file_path_basic,
            args.description,
            client,
            f"{args.description}_{args.model_name}_{args.filename}",
        )

    elif args.prompt_category == "all":
        if  args.article_category == "single":
            # Process and upload basic data
            basic_data = process_single_data(raw_text, target_prompts, prompt_basic_list)
            process_save_upload(
                basic_data,
                jsonl_file_path_basic,
                args.description,
                client,
                f"{args.description}_{args.model_name}_{args.filename}",
            )

            # Process and upload impact data
            impact_data = process_single_data(raw_text, target_prompts, prompt_impact_list)
            process_save_upload(
                impact_data,
                jsonl_file_path_impact,
                args.description,
                client,
                f"{args.description}_{args.model_name}_{args.filename}",
            )

        elif  args.article_category == "multi":
            
             data = process_multi_data(raw_text, V_7_1_m)
             process_save_upload(
                            data,
                            jsonl_file_path_impact,
                            args.description,
                            client,
                            f"{args.description}_{args.model_name}_{args.filename}",
                        )

    

