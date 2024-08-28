# checking the status of batch and retrive the results
import argparse
import os
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
        help="The directory where the LLM outputs will land (as .json)",
        type=str,
    )
    args = parser.parse_args()
    logger.info(f"Passed args: {args}")
    """
    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    """

    env_path = Path(args.api_env)
    load_dotenv(dotenv_path=env_path)
    client = openai.OpenAI(api_key=os.getenv("API_KEY"))
    # return the batches information, and access the ids
    batches = client.batches.list()
    for batch in batches:
        id = batch.id
        client.batches.retrieve(id)

    # checking the status of the batch
    # need to get the id from the batch project
    # client.batches.retrieve("batch_abc123")

    # get output, also need to know the file id in the batch file
    # file_response = client.files.content("file-xyz123")
