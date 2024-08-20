import os
from json.decoder import JSONDecodeError
from pathlib import Path

import openai
from dotenv import load_dotenv

# Explicitly set the path to the .env file
env_path = Path("/home/nl/Wikimpacts/Database/API_KEYS/API_KEY.env")
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("API_KEY")
openai.api_key = api_key

API_ENDPOINT = "https://api.openai.com/v1/chat/completions"


def completion_4(prompt):
    response = openai.chat.completions.create(
        response_format={"type": "json_object"},
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a climate impact analyst. You will be provided with an article to analyze the detailed impact of a disaster event. Please take your time to read the text thoroughly and conduct the analysis step by step.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,  # randomness to 0
        max_tokens=4096,  # This gpt-4o-2024-05-13 model supports at most 4096 completion tokens
        n=1,
        top_p=1,  # return the max probility result
        stop=None,
    )
    message = response.choices[0].message.content
    return message


import json

# Specify the file path
file_path = input("File for prompting experiments:")
Result_DIR = input("Path for prompting results:")

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)


# Function to process the data
def process_whole_text(data):
    filtered_data = [item for item in data["Whole_Text"] if item["content"] not in [None, ""]]
    result = " ".join([f"header: {item['header']}, content: {item['content']}" for item in filtered_data])
    return result


response_gpt4o = []
for item in data:
    Event_ID = str(item.get("Event_ID"))
    Source = str(item.get("Source"))
    Event_Name = str(item.get("Event_Name"))
    info_box = str(item.get("Info_Box"))
    Whole_text = process_whole_text(item)
    prompt_affected_country_0715 = f"""Based on information box {info_box} and header-content pair article {Whole_text},
      extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article.
      The affected people information can be splited into 3 parts,
      the first is the total number of affected people caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Affected":{{
      - "Total_Affected": "The total number of people who were affected, impacted, or influenced in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of affected people in the article to present the total number of affected people,
         and if no total number of affected people explicitly mentioned or the information is missing, assign 'NULL'."
      - "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total affected people. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of affected people in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Affected_Per_Country":[{{
      - "Country": "Name of the country where the affected people located, and no matter the affected people are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The total number of people who were affected, impacted, or influenced in this level related to the {Event_Name}.
         Do not sum the number of affected people in specific locations from the country to present the total number of affected people for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of affected people in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total affected people in this level. The output should only include the header name."
            }}]
      the third is the specific instance of affected people in the sub-national level caused by the {Event_Name}, make sure to capture all locations with affected people information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Country_Affected":[{{
      - "Country": "Name of the country."
      - "Location": "The specific place within the country where the affected people located, and no matter the affected people are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The number of people who were affected, impacted, or influenced in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the affected people in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """

    event_info = {"Event_ID": Event_ID, "Source": Source, "Event_Name": Event_Name}

    answer_str = completion_4(prompt_affected_country_0715)
    try:
        answer_dict = json.loads(answer_str)
        event_info.update(answer_dict)

    except JSONDecodeError as e:
        event_info["Json_error_Affected"] = str(e)

    response_gpt4o.append(event_info)


# Saving the results for all events to a JSON file
with open(
    Result_DIR + "response_wiki_GPT4o_20240729_test_set_affected.json", "w"
) as json_file:  # this output is general and robust, compare to only ask the all the information per location, this capture more information
    json.dump(response_gpt4o, json_file, indent=4)
