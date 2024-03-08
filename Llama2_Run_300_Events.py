import os
os.environ['CUDA_VISIBLE_DEVICES'] = '3'
# # TODO: set your huggingface cache directory. For dgxrise cluster, download large models to raid/ instead of home/ directory
# os.environ["HF_HOME"] = ""

import gc
import time
import urllib.parse
import wikipediaapi
import csv
import torch
import pickle
import re
import pandas as pd
import textwrap
import transformers
import json
from datetime import datetime
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.chains.sequential import SequentialChain, SimpleSequentialChain


MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"


def generate_exp_log(out_dir, file_name, infobox_prompt_template, full_text_update_prompt_template, device=None):
    timestamp = datetime.now().strftime("%m%d%H%M")
    if not os.path.exists(f'{out_dir}{timestamp}/'):
        os.makedirs(f'{out_dir}{timestamp}/')

    with open(f'{out_dir}{timestamp}/{file_name}.txt', 'w') as file:
        file.write(f"Device: {device}\n\n")
        file.write("="*20+"Info Box Prompt Template"+"="*20)
        file.write(f"\n{infobox_prompt_template}\n\n")
        file.write("="*20+"Full Text Update Prompt Template"+"="*20)
        file.write(f"\n{full_text_update_prompt_template}\n\n")

    return timestamp


def generate_output_file(out_dir, url, event_id, page_title, results, time):

    with open(f'{out_dir}{event_id}-InfoBox.txt', 'w') as file:
        file.write(f"Page Url: {url}\n")
        file.write(f"Page Title: {page_title}\n")
        file.write(f"Processing Time: {time}s\n\n\n")

        file.write("="*20+"Output with Info Box Information Only"+"="*20)
        file.write(f"\n{results['infobox_output']}\n\n")

    with open(f'{out_dir}{event_id}-FullText.txt', 'w') as file:
        file.write(f"Page Url: {url}\n")
        file.write(f"Page Title: {page_title}\n\n")
        file.write(f"Processing Time: {time}s\n\n")

        file.write("="*20+"Output Updated with Full Text"+"="*20)
        file.write(f"\n{results['full_text_updated']}\n\n")


def generate_time_consumption_log(out_dir, time, id, is_total_time=False):
    with open(f'{out_dir}time_consumption.txt', 'a') as file:
        if is_total_time:
            file.write(f"\nTotal Time Consumption, {time}")
        else:
            file.write(f"{id}, {time}\n")


def init_model():

    # TODO: set your huggingface access token
    access_token = ''

    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME,
                                                 device_map='auto',
                                                 torch_dtype=torch.bfloat16,
                                                 load_in_4bit=True,
                                                 bnb_4bit_quant_type="nf4",
                                                 bnb_4bit_compute_dtype=torch.bfloat16,
                                                 token=access_token
                                                 )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=access_token)

    pipe = pipeline("text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    torch_dtype=torch.bfloat16,
                    device_map="auto",
                    max_new_tokens=400,
                    do_sample=True,
                    top_k=1,
                    num_return_sequences=1,
                    eos_token_id=tokenizer.eos_token_id
                    )

    llm = HuggingFacePipeline(pipeline=pipe, model_kwargs={'temperature': 0.7, 'max_length': 5000, 'top_k': 1})

    return llm


infobox_prompt_template = """
<s>[INST] rule:
Your task is to analyze the Wikipedia article about "{event_name}" and extract information from its infobox. 

Here are the specific details to look for in the infobox:
- Location: all places affected by the event.
- Single_Date: Assign 'NULL' if the event does not occur and last for only one day.
- Start_Date: The start date of the event, if available; otherwise 'NULL'.
- End_Date: The end date of the event, if available; otherwise 'NULL'.
- Total_Death: Include all people dead in the event, directly or indirectly.
- Num_Injured: Include all people injured in the event, directly or indirectly.
- Num_Displaced: Include all people displaced in the event.
- Num_Homeless: Include all people left homeless by the event.
- Num_Affected: Include all people affected by the event.
- Insured_Damage: The insurance damage amount.
- Insured_Damage_Units: Currency of the insured damage, like USD, EUR.
- Insured_Damage_Inflation_Adjusted: 'Yes' or 'No'.
- Insured_Damage_Inflation_Adjusted_Year: The year for inflation adjustment, if applicable.
- Total_Damage: The total economic loss or damage.
- Total_Damage_Units: Currency of the total damage.
- Total_Damage_Inflation_Adjusted: 'Yes' or 'No'.
- Total_Damage_Inflation_Adjusted_Year: The year for inflation adjustment, if applicable.
- Buildings_Damaged: The total number of buildings damaged.

here is an example:
infobox:
    Formed: 16 April 2006
    Remnant low: 24 April 2006
    Dissipated: 28 April 2006
    Highest winds: 285 km/h (180 mph)
    Lowest pressure: 879 hPa (mbar); 25.96 inHg
    Fatalities: None
    Damage: $5.1 million (2006 USD)
    Areas affected: Papua New Guinea, Queensland, Northern Territory
output:
    "Location": "Papua New Guinea, Queensland, Northern Territory",
    "Single_Date": "NULL"
    "Start_Date": 16 April 2006
    "End_Date":28 April 2006
    "Total_Death": 0,
    "Num_Injured": "NULL",
    "Num_Displaced": "NULL",
    "Num_Homeless": "NULL",
    "Num_Affected": "NULL",
    "Insured_Damage": "NULL",
    "Insured_Damage_Units": "NULL",
    "Insured_Damage_Inflation_Adjusted": "NULL",
    "Insured_Damage_Inflation_Adjusted_Year": "NULL",
    "Total_Damage": 5100000,
    "Total_Damage_Units": "USD",
    "Total_Damage_Inflation_Adjusted": "Yes",
    "Total_Damage_Inflation_Adjusted_Year": "2006",
    "Buildings_Damaged": "NULL",

Please read the infobox content: "{info_box}", and generate the information in JSON format. 
If any information is missing, assign it with "NULL".[/INST]
"""
full_text_update_prompt_template = """
I have analyzed a Wikipedia article about an event and extracted some information, but some details are missing. Below is the information I have extracted so far:

{infobox_output}

The whole text of the article is as follows:

{article}

And the content of the infobox is:

{info_box}

Here are the specific details to look for in the infobox and the whole text:
    - Location
    - Single_Date
    - Start_Date
    - End_Date
    - Total_Death
    - Num_Injured
    - Num_Displaced
    - Num_Homeless
    - Num_Affected
    - Insured_Damage
    - Insured_Damage_Units
    - Insured_Damage_Inflation_Adjusted
    - Insured_Damage_Inflation_Adjusted_Year
    - Total_Damage
    - Total_Damage_Units
    - Total_Damage_Inflation_Adjusted
    - Total_Damage_Inflation_Adjusted_Year
    - Buildings_Damaged
    
[INST]Based on this information, please fill in the missing details in the JSON structure.
If you find more information in the whole text than infobox, please update the result.
If a piece of information is truly unavailable in the text or infobox, leave it as "NULL".
Don't generate any other text except the JSON object.[/INST]
"""


def get_info_by_id(dataset_path, id):
    url, info_box = None, None

    with open(dataset_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)

        # Skip the header
        next(reader)

        for row in reader:
            if int(row[0]) == id:
                url = urllib.parse.unquote(row[1])
                info_box = row[2]
                break

    return url, info_box


wiki_api_instance = wikipediaapi.Wikipedia(
    user_agent='ImpactDB (chanjuan@kth.se)',
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)


def get_info_box_and_full_text_by_id(id, dataset_path='./data/300_events/300_events_infobox.csv', wiki_api_instance=wiki_api_instance):

    url, info_box = get_info_by_id(dataset_path, id)
    page_title = url.replace('https://en.wikipedia.org/wiki/', '')
    full_text = wiki_api_instance.page(page_title).text

    return info_box, full_text, page_title, url


def main():
    main_start_time = time.time()
    mistral = init_model()

    infobox_prompt = PromptTemplate(template=infobox_prompt_template, input_variables=["event_name", "info_box"])
    infobox_chain = LLMChain(llm=mistral, prompt=infobox_prompt, output_key="infobox_output")
    full_text_update_prompt = PromptTemplate(template=full_text_update_prompt_template, input_variables=[
        "infobox_output", "article", "info_box"])
    full_text_update_chain = LLMChain(llm=mistral, prompt=full_text_update_prompt, output_key="full_text_updated")

    sequential_chain = SequentialChain(chains=[infobox_chain, full_text_update_chain], input_variables=[
        "event_name", "info_box", "article"], output_variables=["infobox_output", "full_text_updated"])
    out_dir = './results/Llama2-300-Main-Events/'
    timestamp = generate_exp_log(out_dir, "Llama2-7B-chat",
                                 infobox_prompt_template, full_text_update_prompt_template, device="cuda: 3")

    times = []
    for id in range(0, 245, 1):
        start_time = time.time()
        info_box, full_text, page_title, url = get_info_box_and_full_text_by_id(id)
        event_name = page_title.replace('_', ' ')

        if len(full_text) > 10000:
            full_text = full_text[:10000]

        print("Event ", id)
        print("URL:", url)
        print("Event Name:", event_name)

        results = sequential_chain({"event_name": event_name, "info_box": info_box, "article": full_text})
        end_time = time.time()
        elapsed_time = end_time - start_time
        times.append(elapsed_time)
        generate_time_consumption_log(out_dir+f'{timestamp}/', elapsed_time, id, is_total_time=False)
        print(f"Time Consumption: {elapsed_time} s")

        generate_output_file(out_dir+f'{timestamp}/', url, id, page_title, results, elapsed_time)
        gc.collect()
        torch.cuda.empty_cache()

    main_end_time = time.time()
    main_elapsed_time = main_end_time-main_start_time
    generate_time_consumption_log(out_dir+f'{timestamp}/', main_elapsed_time, id, is_total_time=True)
    print(f"All articles are processed! Total time comsumption: {main_elapsed_time}")


if __name__ == '__main__':
    main()
