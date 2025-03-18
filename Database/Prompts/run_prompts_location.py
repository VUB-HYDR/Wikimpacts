import os
import sys


pythonpath = os.path.abspath(os.path.dirname(os.path.dirname(__name__)))

sys.path.insert(0, pythonpath)

import pathlib
from pathlib import Path
from Evaluation_V2.comparer import Comparer
from Database.Prompts.prompts import generate_LocationEvent, Post_location
from Database.Prompts.run_prompts_v2 import update_location_chains_for_specific_columns

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

    args = parser.parse_args()
    logger.info(f"Passed args: {args}")

    logger.info(f"Creating {args.output_dir} if it does not exist!")

    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)
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
    Comp =Comparer()
    # First loop: Extract and normalize locations
    for index, item in df.iterrows():
        Locations = item["Locations"]
        country = item["country"]
        user_input = f"Country: {country}, a list of locations: {Locations}."
        
        res_format = generate_LocationEvent()
        Locations_chain = gpt_completion(res_format, user_input, Post_location)
        
        # Normalize and store result in df_dev
        df.loc[index, "Locations_chain_LLM"] = Norm.sequence(Locations_chain)

    # Second loop: Compare scores
    for index, item in df.iterrows():
        score = Comp.sequence(item["Locations_chain_LLM"], item["Locations_chain"])
        df.loc[index, "Score"] = score

    # Return the final DataFrame
    df.to_csv(f"{args.output_dir}/{args.filename}")
