import argparse
import asyncio
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
    API_ENDPOINT = "https://api.openai.com/v1/chat/completions"

    async def get_gpt_response_basic(model_name, prompt):
        response = await openai.chat.completions.create(
            model=args.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a climate scientist. You will be provided with an article to analyze the basic information of a disaster event. Please take your time to read the text thoroughly and conduct the analysis step by step.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,  # randomness
            max_tokens=4096,  # This model supports at most 4096 completion tokens
            n=1,
            top_p=1,  # return the max probility result
            stop=None,
        )
        for choice in response.choices:
            if choice.message.role == "assistant":
                gpt_output = choice.message.content.strip()
                gpt_output = gpt_output.replace("```json", "").replace("```", "").strip('"').strip()
                try:
                    return json.loads(gpt_output)
                except:
                    try:
                        ## an ugly hack for a persistent json error with main events
                        gpt_output = gpt_output.replace("\n}\n\n\n{", ",")
                        return json.loads(gpt_output)
                    except:
                        return {"error": gpt_output}
        raise Exception  # or raise an Exception

    async def process_batch(event_prompts, output_file):
        meta_dict, prompts = event_prompts
        gpt_tasks = [get_gpt_response_basic(args.model_name, prompt) for prompt in prompts]
        gpt_output = await asyncio.gather(*gpt_tasks, return_exceptions=True)
        final_output = meta_dict
        for o in gpt_output:
            final_output.update(o)
        return final_output
