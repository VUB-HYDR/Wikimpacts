import asyncio
import json
import os
import time

import aiofiles
from openai import AsyncOpenAI
from fine_tune import key
from utils import load_wiki_content, prompts_dict, prepare_prompt

model_name = "gpt-4o-mini"
client = AsyncOpenAI(
    api_key=key
)


async def get_gpt_response(model_name, prompt):
    response = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )
    for choice in response.choices:
        if choice.message.role == "assistant":
            gpt_output = choice.message.content.strip()
            gpt_output = gpt_output.replace("```json", '').replace("```", "").strip("\"").strip()
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
    gpt_tasks = [get_gpt_response(model_name, prompt) for prompt in prompts]
    gpt_output = await asyncio.gather(*gpt_tasks, return_exceptions=True)
    final_output = meta_dict
    for o in gpt_output:
        final_output.update(o)
    return final_output


async def main():
    wiki_json = "wikipedia/wiki_dev_whole_infobox_20240710.json"
    wiki_articles = load_wiki_content(wiki_json)
    prompts_list = {}
    threshold = None  # for debugging, limits the number of articles to be processed

    gpt_output_file = f"{model_name}_output_dev.json"
    all_gpt_output = []
    processed_event_ids = set()
    # Check if the output file already exists and load processed event IDs
    if os.path.exists(gpt_output_file):
        with open(gpt_output_file, mode='r') as f:
            existing_data = json.load(f)
            processed_event_ids.update([entry["Event_ID"] for entry in existing_data])
            all_gpt_output.extend([entry for entry in existing_data])
        print(f"Loaded {len(existing_data)} previously processed events from {gpt_output_file}.")

    else:
        processed_event_ids = ()

    for article in wiki_articles.values():
        event_id = article["Event_ID"]
        if event_id in processed_event_ids: continue
        if threshold and len(prompts_list) >= threshold: break
        meta_dict = {"Event_ID": event_id, "Source": article["Source"], "Event_Name": article["Event_Name"]}
        prompts = [prepare_prompt(article, p) for p in prompts_dict]
        prompts_list[event_id] = (meta_dict, prompts)
    print(f"Prepared {len(prompts_list)} new events for processing.")

    gpt_output_file = f"{model_name}_output_dev.json"
    try:
        for event_id, event_prompts in prompts_list.items():
            print(f"{len(event_prompts[1])} prompts are running for Event ID: {event_id}", end=" -> ")
            start_time = time.time()
            batch_output = await process_batch(event_prompts, gpt_output_file)
            all_gpt_output.append(batch_output)
            print(f"took {time.time() - start_time } seconds")
            await asyncio.sleep(1)  # Sleep between batches to respect rate limits
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Save accumulated results in case of an error
        async with aiofiles.open(gpt_output_file, mode='w') as f:
            await f.write(json.dumps(all_gpt_output, indent=4))

asyncio.run(main())
