import json, csv
# Function to load scores from CSV file
def load_scores(csv_file):
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        processed_rows = {}
        for row in csv_reader:
            try:
                event_id = int(float(row['Event_ID1']))
            except:
                event_id = row['Event_ID1']
            processed_row = {event_id: {
                'Total_Summary_Death': (float(row['Total_Deaths_Min']) + float(row['Total_Deaths_Max'])) / 2,
                'Total_Summary_Injury': (float(row['Total_Injuries_Min']) + float(row['Total_Injuries_Max'])) / 2,
                'Total_Summary_Building_Damage': (float(row['Total_Buildings_Min']) + float(row['Total_Buildings_Max'])) / 2,
                'Total_Summary_Affected': (float(row['Total_Affected_Min']) + float(row['Total_Affected_Max'])) / 2,
                'Total_Summary_Homeless': (float(row['Total_Homeless_Min']) + float(row['Total_Homeless_Max'])) / 2,
                'Total_Summary_Displace': (float(row['Total_Displace_Min']) + float(row['Total_Displace_Max'])) / 2,
                'Total_Summary_Economic_Damage': (float(row['Total_Damage_Min']) + float(row['Total_Damage_Max'])) / 2,
                'Total_Summary_Insured_Damage': (float(row['Total_Insured_Damage_Min']) + float(row['Total_Insured_Damage_Max'])) / 2,
                'Main_Event': float(row['Main_Event']),
                'Start_Date': (float(row['Start_Date_Day']) + float(row['Start_Date_Month']) + float(row['Start_Date_Year'])) / 3,
                'End_Date': (float(row['End_Date_Day']) + float(row['End_Date_Month']) + float(row['End_Date_Year'])) / 3,
            }}
            processed_rows.update(processed_row)
    return processed_rows


# Function to load predictions from JSON file
def load_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
        try:
            data = {int(float(event['Event_ID'])): event for event in data}
        except:
            data = {event['Event_ID']: event for event in data}

    return data


def load_wiki_content(wiki_file):
    def process_whole_text(article):
        filtered_data = [item for item in article["Whole_Text"] if item["content"] not in [None, ""]]
        result = " ".join([f"header: {item['header']}, content: {item['content']}" for item in filtered_data])
        return result

    with open(wiki_file, 'r') as file:
        data = json.load(file)
        for article in data:
            article["Whole_text"] = process_whole_text(article)
    try:
        data = {int(float(event['Event_ID'])): event for event in data}
    except:
        data = {event['Event_ID']: event for event in data}
    return data


def create_training_instance(user_content, assistant_content, event_id = None):
    completion_suffix = ""
    system_content = "You are an intelligent assistant specialized in extracting accurate and comprehensive " \
                     "information about the impacts of extreme climate events from textual sources."
    assistant_content = " " + assistant_content + completion_suffix
    if "xxxxxxNULL" in assistant_content:
        return None
    return {
        "messages": [
            {"role": "system", "content": system_content if not event_id else event_id},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content}
        ]
    }


# Function to create training data in JSONL format
def prepare_prompt(wiki, prompt_type):
    data_for_prompt = {
        "info_box": wiki["Info_Box"],
        "Whole_text": wiki["Whole_text"],
        "Event_Name": wiki["Event_Name"]
    }
    prompt = prompts_dict[prompt_type].format_map(data_for_prompt)
    return prompt

prompt_affected_country_0715 = """Based on information box {info_box} and header-content pair article {Whole_text},
extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article.
The total number of affected people caused by the {Event_Name}, and organize this information in JSON format as follows:
- "Total_Summary_Affected":{{
- "Total_Affected": "The total number of people who were affected, impacted, or influenced in the {Event_Name}.
Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
Do not sum the number of affected people in the article to present the total number of affected people,
and if no total number of affected people explicitly mentioned or the information is missing, assign 'NULL'."
- "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total affected people. The output should only include "Info_Box" or the header name."
}}
Ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """

prompt_building_damage_country_0715 = """Based on the provided article {info_box} {Whole_text},
extract the number of damaged buildings associated with the {Event_Name},
covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
along with supporting annotations from the article. The total number of damaged buildings caused by the {Event_Name}, and organize this information in JSON format as follows:
- "Total_Summary_Building_Damage":{{
- "Total_Building_Damage": "The total number of damaged buildings in the {Event_Name}.
Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
Do not sum the number of damaged buildings in the article to present the total number of damaged buildings,
and if no total number of damaged buildings explicitly mentioned or the information is missing, assign 'NULL'."
- "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total number of damaged buildings. The output should only include "Info_Box" or the header name."
}}
Ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """

prompt_death_country_0715 = """Based on information box {info_box} and header-content pair article {Whole_text}, extract the number of deaths associated with the {Event_Name},
along with supporting annotations from the article. The total number of deaths caused by the {Event_Name}, and organize this information in JSON format as follows:
- "Total_Summary_Death":{{
- "Total_Death": "The total number of people who died in the {Event_Name}.
Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
Do not sum the number of death in the article to present the total number of death, and if no total number of death explicitly mentioned or the information is missing, assign 'NULL'."
- "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total death. The output should only include "Info_Box" or the header name."
}}
Ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """

prompt_displace_country_0715 = """Based on information box {info_box} and header-content pair article {Whole_text},
extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article.
The total number of displacement caused by the {Event_Name}, and organize this information in JSON format as follows:
- "Total_Summary_Displace":{{
- "Total_Displace": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the {Event_Name}.
Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
Do not sum the number of displacement in the article to present the total number of displacement,
and if no total number of displacement explicitly mentioned or the information is missing, assign 'NULL'."
- "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total displacement. The output should only include "Info_Box" or the header name."
}}
Ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """

prompt_homeless_country_0715 = """Based on information box {info_box} and header-content pair article {Whole_text},
extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article.
The total number of homelessness caused by the {Event_Name}, and organize this information in JSON format as follows:
- "Total_Summary_Homeless":{{
- "Total_Homeless": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the {Event_Name}.
Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
Do not sum the number of homelessness in the article to present the total number of homelessness,
and if no total number of homelessness explicitly mentioned or the information is missing, assign 'NULL'."
- "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total homelessness. The output should only include "Info_Box" or the header name."
}}
Ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """

prompt_injury_country_0715 = """Based on information box {info_box} and header-content pair article {Whole_text},
extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article.
The total number of non-fatal injuries caused by the {Event_Name}, and organize this information in JSON format as follows:
- "Total_Summary_Injury":{{
- "Total_Injury": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in the {Event_Name}.
Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
Do not sum the number of non-fatal injuries in the article to present the total number of non-fatal injuries,
and if no total number of non-fatal injuries explicitly mentioned or the information is missing, assign 'NULL'."
- "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total non-fatal injuries. The output should only include "Info_Box" or the header name."
}}
Ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """

prompt_insure_per_country_0715 = """
Based on information box {info_box} and header-content pair article {Whole_text},
extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article.
The total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy,
and organize this information in JSON format as follows:
- "Total_Summary_Insured_Damage": {{
- "Total_Insured_Damage": "The total amount of insured damage and make sure the information extracted for this containing the keyword "insured" or "insurance".
   Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
   Do not sum the number of insured damage in the article to present the total number of insured damage,
   and if no total number of insured damage explicitly mentioned or the information is missing, assign 'NULL'."
- "Units": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
- "Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
- "Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
- "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total insured damage. The output should only include "Info_Box" or the header name."
}}
Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """

prompt_location_time_0715 = """
Based on information box {info_box} and header-content pair article {Whole_text}, extract time and location information associated with the {Event_Name}, along with supporting annotations from the article.
the first is to identify the time information of the event {Event_Name}, and organize this information in JSON format as follows:
- "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
- "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
- "Time_with_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the time. The output should only include "Info_Box" or the header name."
the second is to identify all locations affected by {Event_Name} and organize this information in JSON format as follows:
- "Location": "List all places mentioned in the text, including cities, regions, countries, and other administrative locations affected by {Event_Name}. The list should be formatted as ["location1", "location2"]."
- "Location_with_Annotation":  "Cite "Info_Box" or the header name from the article provided where you find the information about the affected locations. The output should only include "Info_Box" or the header name."
Only Give Json output, no extra explanation needed."""

prompt_main_event_hazard_0715 = """
Based on information box {info_box} and header-content pair article {Whole_text},
extract main_event category and hazard information associated with the {Event_Name}, along with supporting annotations from the article.
Below is the Main_Event--Hazard association table,
Main Event: Flood; Hazard: Flood
Main Event: Extratropical Storm/Cyclone; Hazards: Wind; Flood; Blizzard; Hail
Main Event: Tropical Storm/Cyclone; Hazards: Wind; Flood; Lightning
Main Event: Extreme Temperature; Hazards: Heatwave; Cold Spell
Main Event: Drought; Hazard: Drought
Main Event: Wildfire; Hazard: Wildfire
Main Event: Tornado; Hazard: Wind
first identify the Main_Event category information from the text, and organize this information in JSON format as follows:
- "Main_Event": "identify the event category of the {Event_Name} referring the Main_Event--Hazard table, and only one Main_Event category should be assigned."
- "Main_Event_Assessment_With_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the Main_Event category. The output should only include "Info_Box" or the header name."
based on the result of the Main_Event category from the previous step and the Main_Event--Hazard table, identify the hazard information and organize this information in JSON format as follows:
- "Hazard": "Identify the hazard of the {Event_Name}, make sure the hazard is associated with the Main_Event category from the table, and if more than one hazard is detected from the text, separate them with '|'. "
- "Hazard_Assessment_With_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the hazard information. The output should only include "Info_Box" or the header name."
Only Give Json output, no extra explanation needed."""

prompt_economic_per_country_0715 = """"
Based on information box {info_box} and header-content pair article {Whole_text},
extract the economic damage information associated with the {Event_Name}, along with supporting annotations from the article.
Organize the total economic damage caused by the {Event_Name} in JSON format as follows:
- "Total_Summary_Economic_Damage": {{
- "Total_Economic_Damage": "The total amount of economic damage.
   Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
   Do not sum the number of economic damage in the article to present the total number of economic damage,
   and if no total number of economic damage explicitly mentioned or the information is missing, assign 'NULL'."
- "Units": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
- "Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
- "Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
- "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total economic damage. The output should only include "Info_Box" or the header name."
}}
Ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """

suffix = ""

prompts_dict = {
    "prompt_affected_country_0715": prompt_affected_country_0715 + suffix,
    "prompt_building_damage_country_0715": prompt_building_damage_country_0715 + suffix,
    "prompt_death_country_0715": prompt_death_country_0715 + suffix,
    "prompt_displace_country_0715": prompt_displace_country_0715 + suffix,
    "prompt_homeless_country_0715": prompt_homeless_country_0715 + suffix,
    "prompt_injury_country_0715": prompt_injury_country_0715 + suffix,
    "prompt_insure_per_country_0715": prompt_insure_per_country_0715 + suffix,
    "prompt_location_time_0715": prompt_location_time_0715 + suffix,
    "prompt_main_event_hazard_0715": prompt_main_event_hazard_0715 + suffix,
    "prompt_economic_per_country_0715": prompt_economic_per_country_0715 + suffix
}

prompt_mapping = {
    "Total_Summary_Affected": 'prompt_affected_country_0715',
    "Total_Summary_Building_Damage": 'prompt_building_damage_country_0715',
    "Total_Summary_Death": 'prompt_death_country_0715',
    "Total_Summary_Displace": 'prompt_displace_country_0715',
    "Total_Summary_Homeless": 'prompt_homeless_country_0715',
    "Total_Summary_Injury": 'prompt_injury_country_0715',
    "Total_Summary_Economic_Damage": 'prompt_economic_per_country_0715',
    "Total_Summary_Insured_Damage": 'prompt_insure_per_country_0715',
    "Main_Event": 'prompt_main_event_hazard_0715',
    "Start_Date": 'prompt_location_time_0715'
}