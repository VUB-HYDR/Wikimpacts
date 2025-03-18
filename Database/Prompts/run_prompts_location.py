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
from Evaluation_V2.comparer import Comparer
from Database.Prompts.prompts import generate_LocationEvent, Post_location


from Evaluation_V2.normaliser import Normaliser

import pandas as pd 
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
        help="The directory for the output file",
        type=str,
    )
       # Explicitly set the path to the .env file
    parser.add_argument(
        "-null",
        "--null_penalty",
        dest="null_penalty",
        default=1,
        help="Null penalty, defaults to 1",
        type=float,
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
    

    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    env_path = Path(args.api_env)
    load_dotenv(dotenv_path=env_path)
    client = openai.OpenAI(api_key=os.getenv("API_KEY"))

    # loading csv or json files 
    if args.filename.endswith(".json"):
       with open(f"{args.raw_dir}/{args.filename}", "r") as file:
        # Step 2: Load the JSON data into a Python dictionary
           df = json.load(file)
    else: 
       df=pd.read_csv(f"{args.raw_dir}/{args.filename}")
    # Evaluate the location extraction 



    # Normalizer object (initialized once)
    Norm = Normaliser()
    null_penalty = args.null_penalty
    
    def sequence( v, w):
        """Compare sequences. Returns Jaccard distance between sets of elements in sequences.
        Note: ordering is not taken into consideration."""
        if v == None and w == None:
            return 0
        if v == None and w != None or v != None and w == None:
            return null_penalty
        v = set(v)
        w = set(w)

        union_len = len(v.union(w))
        if union_len == 0:
            return 0.0
        return 1.0 - len(v.intersection(w)) / union_len
    # First loop: Extract and normalize locations
    for index, item in df.iterrows():
        Locations = item["Locations"]
        country = item["country"]
        user_input = f"Country: {country}, a list of locations: {Locations}."
        
        res_format = generate_LocationEvent()
        Locations_chain = gpt_completion(res_format, user_input, Post_location)
        
        # Normalize and store result in df_dev
        df.loc[index, "Locations_chain_LLM"] = Locations_chain

    # Second loop: Compare scores
    for index, item in df.iterrows():
        
       
        data_list=item["Locations_chain_LLM"]
        print(data_list)
        print(type(data_list))
        if isinstance(data_list, str):
            try:
                data_list = json.loads(data_list)  # Convert to dict
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON at row {index}")
                data_list = {}

        # Step 2: Extract "Location_Chains" safely
        LLM_locations = set()
        if isinstance(data_list, dict) and "Location_Chains" in data_list:
            location_chains = data_list["Location_Chains"]
            
            if isinstance(location_chains, list):  # Ensure it's a list
                if isinstance(location_chains[0], list):  # List of lists case
                    LLM_locations = {loc for sublist in location_chains for loc in (sublist if isinstance(sublist, list) else [sublist])}
                    
        
         
        LLM_norm = sorted(LLM_locations)
        print(LLM_norm)
        gold = Norm.sequence(item["Locations_chain"])
        #print(LLM_norm, gold)
        score = sequence(LLM_norm, gold)
        df.loc[index, "Score"] = score

    # Return the final DataFrame
    df.to_csv(f"{args.output_dir}/{args.filename}")
