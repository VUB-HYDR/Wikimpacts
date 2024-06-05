import json
import time

# This file is only to share the prompts
Wiki_text = ""

# Initialize an empty list to store execution times
execution_times = []
response_wiki_GPT4=[]


 # Start the timer
start_time = time.time()
Source = str(Wiki_text['Source'])
Event_Name = str(Wiki_text['Event_Name'])
#print(Event_Name)
Whole_text = str(Wiki_text['Whole_Text'])
info_box=str(Wiki_text['Info_Box'])

prompt_main_event=f'''Based on the provided article {info_box} {Whole_text}, please extract information about the main event {Event_Name} , and assign the details as follows:
- "Main_Event": "identify the event category referring to "Extratropical Storm/Cyclone; Tropical Storm/Cyclone; Extreme Temperature;
  Drought; Wildfire; Tornado". Only one category should be assigned."
- "Main_Event_Assessment_With_Annotation": "Include text from the original text that supports your findings on the Main_Event."
please give the json format output of these two items above, and please make sure that your annotation text is explicitly from the original text provided.
'''
prompt_perils=f'''Based on the provided article {info_box} {Whole_text}, please extract information about the perils {Event_Name} , and assign the details as follows:
- "Perils": "identify the perils referring to "Wind; Rainfall; Flood; Landfall; Landslide; Blizzard; Hail; Lightning; Thunderstorm; Heatwave; Cold Spell/Cold Snap; Drought; Wildfire". 
If more than one peril is detected from the text, separate them with "|". "
- "Perils_Assessment_With_Annotation": "Include text from the original text that supports your findings on the perils. "
please give the json format output of these two items above, and please make sure that your annotation text is explicitly from the original text provided.
'''

prompt_location = f'''
Based on the provided article {info_box} {Whole_text}, identify all locations affected by {Event_Name} and assign the appropriate details.
- "Location": "List all places mentioned in the text as being affected by  {Event_Name} ."
- "Location_with_Annotation": "For each location listed, include a snippet from the article that supports why you consider it affected by  {Event_Name} . This annotation should help illustrate how you determined the location was impacted. This should directly quote the original text."
please give the json format output of these two items above, and please make sure that your annotation text is explicitly from the original text provided.
'''
prompt_country = f'''
Based on the provided article {info_box} {Whole_text}, identify all countries affected by {Event_Name} 
and assign the appropriate details.
- "Country": "List all countries mentioned in the text as being affected by  {Event_Name}."
- "Country_with_Annotation": "For each location listed, include a snippet from the article that supports why you consider it affected by {Event_Name}. This annotation should help illustrate how you determined the country was impacted. This should directly quote the original text."
please give the json format output of these two items above, and please make sure that your annotation text is explicitly from the original text provided.
'''


prompt_time = f'''
Based on the provided article {info_box} {Whole_text}, identify the time infomation {Event_Name} described, and assign the appropriate details.
- "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
- "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
- "Time_with_Annotation": "Include text from the original text that supports your findings on the start date and end date. This should directly quote the original text."
please give the json format output of these three items above, and please make sure that your annotation text is explicitly from the original text provided.
'''
# the newest version, same as the one in the paper 
prompt_death_per_country = f'''
Based on the provided article, which includes the information box {info_box} and the full text {Whole_text},
first extract and summarize the total number of deaths associated with {Event_Name}, along with supporting annotations from the article. 
Organize this information in JSON format as follows:
- "Total_Summary_Death":{{
- "Total_Deaths": "The total number of people who died in {Event_Name}, both directly and indirectly. 
Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people'). If the information is missing, assign 'NULL'."
- "Total_Death_Annotation": "Provide excerpts from the article that directly support your findings on the total number of deaths. This should directly quote the original text."
}}
if the "Total_Deaths" is not "NULL" or "0", then, delve deeper to provide a detailed breakdown of these deaths by country, 
the first instance in the "Specific_Instance_Per_Country_Death" section for each country provides a summary of the total deaths within that country and the "Location_Death" is the country name, 
followed by a breakdown into specific cities, towns, or regions where possible. 
Organize this information in JSON format as follows:
- "Specific_Instance_Per_Country_Death":[{{
- "Country": "Name of the country."
- "Location_Death": "The specific place within the country where the deaths occurred, including towns, cities, or regions."
- "Start_Date_Death": "The start date when the deaths occurred, if mentioned."
- "End_Date_Death":"The end date when the deaths occurred, if mentioned."
- "Num_Death": "The number of people who died in this specific location or incident related to {Event_Name}. Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people'). If the information is missing, assign 'NULL'."
- "Death_with_annotation": "Excerpts from the article that support your findings on the location, time, number of deaths. This should directly quote the original text."
       }}]
Ensure to capture all instances of death mentioned in the article, including direct and indirect causes. 
'''


prompt_injuries_per_country = f'''
Based on the provided article, which includes the information box {info_box} and the full text {Whole_text},
first extract and summarize the total number of injuries associated with {Event_Name}, along with supporting annotations from the article.
Organize this information in JSON format as follows:
- "Total_Summary_Injuries": {{
- "Total_Injuries": "The total number of people who were injured in {Event_Name}, both directly and indirectly. Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people'). If the information is missing, assign 'NULL'."
- "Total_Injuries_Annotation": "Provide excerpts from the article that directly support your findings on the total number of injuries. This should directly quote the original text."
}}
If the "Total_Injuries" is not "NULL" or "0", then, delve deeper to provide a detailed breakdown of these injuries by country. 
For the first instance in the "Specific_Instance_Per_Country_Injuries" section for each country, provide a summary of the total injuries within that country and the "Location_Injuries" is the country name, 
followed by a breakdown into specific cities, towns, or regions where possible.
Organize this information in JSON format as follows:
- "Specific_Instance_Per_Country_Injuries": [{{
- "Country": "Name of the country.",    
- "Location_Injuries": "The specific place within the country where the injuries occurred, including towns, cities, or regions.",
- "Start_Date_Injuries": "The start date when the injuries occurred, if mentioned."
- "End_Date_Injuries":"The end date when the injuries occurred, if mentioned."
- "Num_Injuries": "The number of people who were injured in this specific location or incident related to {Event_Name}. Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people'). If the information is missing, assign 'NULL'."
- "Injuries_with_annotation": "Excerpts from the article that support your findings on the location, time, number of injuries, and any additional details for each instance. This should directly quote the original text."
    }}]
Ensure to capture all instances of injuries mentioned in the article, including direct and indirect causes.
'''
prompt_displaced_per_country = f'''
Based on the provided article, which includes the information box {info_box} and the full text {Whole_text},
first extract and summarize the total number of people explicitly displaced by {Event_Name}, along with supporting annotations from the article. Organize this information in JSON format as follows:
- "Total_Summary_Displacement": {{
- "Total_Displacement": "The total number of people displaced by {Event_Name}. Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people'). If the information is missing, assign 'NULL'."
- "Total_Displacement_Annotation": "Provide excerpts from the article that support your findings on the total number of people displaced. This should directly quote the original text."
}}
If the "Total_Displacement" is not "NULL" or "0", then, delve deeper to provide a detailed breakdown of these displacements by country. 
For the first instance in the "Specific_Instance_Per_Country_Displacement" section for each country, provide a summary of the total displacements within that country and the "Location_Displace" is the country name, 
followed by a breakdown into specific cities, towns, or regions where possible. Organize this information in JSON format as follows:
- "Specific_Instance_Per_Country_Displacement": [{{
- "Country": "Name of the country.",
- "Location_Displacement": "The specific place within the country where the displacement occurred, including towns, cities, or regions.",
- "Start_Date_Displacement": "The start date when the displacement occurred, if mentioned."
- "End_Date_Displacement":"The end date when the displacement occurred, if mentioned."
- "Num_Displacement": "The number of people displaced in this specific location or incident related to {Event_Name}. Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people'). If the information is missing, assign 'NULL'."
- "Displacement_with_annotation": "Excerpts from the article that support your findings on the location, time, and number of people displaced for each instance. This should directly quote the original text."
      }}]
Ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes, and organize them in the JSON format output. 
'''

prompt_homeless_per_country = f'''
Based on the provided article, which includes the information box {info_box} and the full text {Whole_text},
first extract and summarize the total number of people explicitly left homeless by {Event_Name}, along with supporting annotations from the article. Organize this information in JSON format as follows:
- "Total_Summary_Homelessness": {{
- "Total_Homelessness": "The total number of people reported as homeless by {Event_Name}. Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people'). If the information is missing, assign 'NULL'."
- "Total_Homelessness_Annotation": "Provide excerpts from the article that support your findings on the total number of people left homeless. This should directly quote the original text."
}}
If the "Total_Homelessness" is not "NULL" or "0", then, delve deeper to provide a detailed breakdown of these instances of homelessness by country. 
For the first instance in the "Specific_Instance_Per_Country_Homelessness" section for each country, provide a summary of the total homelessness within that country and the "Location_Homeless" is the country name, 
followed by a breakdown into specific cities, towns, or regions where possible. Organize this information in JSON format as follows:
- "Specific_Instance_Per_Country_Homelessness": [{{
- "Country": "Name of the country.",
- "Location_Homelessness": "The specific place within the country where the homelessness occurred, including towns, cities, or regions.",
- "Start_Date_Homelessness": "The start date when the homelessness occurred, if mentioned."
- "End_Date_Homelessness":"The end date when the homelessness occurred, if mentioned."
- "Num_Homelessness": "The number of people reported as homeless in this specific location or incident related to {Event_Name}.Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people'). If the information is missing, assign 'NULL'."
- "Homelessness_with_annotation": "Excerpts from the article that support your findings on the location, time, and number of people left homeless for each instance. This should directly quote the original text."
      }}]
Ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes, and organize them in the JSON format output. 
'''
# still process it  
prompt_affected_per_country = f'''
Based on the provided article, which includes the information box {info_box} and the full text {Whole_text} related to {Event_Name},
first extract and summarize the total number of people explicitly mentioned as being 'affected,' 'impacted,' or 'influenced' by {Event_Name}, 
along with supporting annotations from the article. 
Organize this information in JSON format as follows:
- "Total_Summary_Affected": {{
- "Total_Affected": "The total number of people reported as affected by {Event_Name}. Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people'). If the information is missing, assign 'NULL'."
- "Total_Affected_Annotation": "Provide excerpts from the article that support your findings on the total number of people affected. This should directly quote the original text."
}}
If the "Total_Affected" is not "NULL" or "0", then, delve deeper to provide a detailed breakdown of these instances of people being affected by country. 
For the first instance in the "Specific_Instance_Per_Country_Affected" section for each country, provide a summary of the total number of people affected within that country and the "Location_Affect" is the country name, 
followed by a breakdown into specific cities, towns, or regions where possible. Organize this information in JSON format as follows:
- "Specific_Instance_Per_Country_Affected": [{{
- "Country": "Name of the country.",
- "Location_Affected": "The specific place within the country where the affected people are located, including towns, cities, or regions.",
- "Start_Date_Affected": "The start date when the people were affected, if mentioned."
- "End_Date_Affected":"The end date when the people were affected, if mentioned."
- "Num_Affected": "The number of people affected in this specific location or incident related to {Event_Name}.Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people'). If the information is missing, assign 'NULL'."
- "Affected_with_annotation": "Excerpts from the article that support your findings on the location, time, and number of people affected for each instance. This should directly quote the original text."
      }}]
Ensure to capture all instances of people being affected mentioned in the article, including direct and indirect causes, and organize them in the JSON format output. 
'''
prompt_insure_per_country = f'''
Based on the provided article, which includes the information box {info_box} and the full text {Whole_text} related to {Event_Name},
first extract and summarize the total insured damage reported due to {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy, along with supporting annotations from the article. Organize this information in JSON format as follows:
- "Total_Summary_Insured_Damage": {{
- "Total_Insured_Damage": "The total amount of insured damage. Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
- "Total_Insured_Damage_Units": "The currency of the total insured damage, like USD, EUR. If not specified, assign 'NULL'."
- "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total damage amount has been adjusted for inflation; otherwise, 'No'."
- "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total damage, if applicable. If not adjusted or not applicable, assign 'NULL'."
- "Total_Insured_Damage_Assessment_with_annotation": "Provide excerpts from the article that support your findings on the total amount of insured damage. This should directly quote the original text."
}}
If the "Total_Insured_Damage" is not "NULL" or "0", then, delve deeper to provide a detailed breakdown of insured damages by country. 
For the first instance in the "Specific_Instance_Per_Country_Insured_Damage" section for each country, provide a summary of the total insured damages within that country and the "Location_Insured_Damage" is the country name, 
followed by a breakdown into specific cities, towns, or regions where possible.
Organize this information in JSON format as follows:
- "Specific_Instance_Per_Country_Insured_Damage": [{{
- "Country": "Name of the country.",
- "Location_Insured_Damage": "The specific place within the country where the insured damage occurred, including towns, cities, or regions." 
- "Insured_Damage": "The amount of insured damage.",
- "Insured_Damage_Units": "The currency of the insured damage, like USD, EUR. If not specified, assign 'NULL'."
- "Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the damage amount has been adjusted for inflation; otherwise, 'No'."
- "Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment, if applicable. If not adjusted or not applicable, assign 'NULL'."
- "Insured_Damage_Assessment_with_annotation": "Include text from the original article that supports your findings on the insured damage amount and details for each instance. This should directly quote the original text."
      }}]
Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes, and organize them in the JSON format output.
'''
prompt_total_per_country = f'''
Based on the provided article, which includes the information box {info_box} and the full text {Whole_text} related to {Event_Name},
first extract and summarize detailed information about the total economic loss or damage caused by {Event_Name}, focusing specifically on the economic impact in the mentioned regions. The information should be organized in JSON format as follows:
- "Total_Summary_Damage": {{
- "Total_Damage": "Specify the economic loss or damage reported. If this information is not mentioned, assign 'NULL'."
- "Total_Damage_Units": "Indicate the currency of the reported damage (e.g., USD, EUR). If the currency is not specified, assign 'NULL'."
- "Total_Damage_Inflation_Adjusted": "State 'Yes' if the reported damage amount has been adjusted for inflation; otherwise, indicate 'No'. If this aspect is not mentioned, provide your best judgment based on the context."
- "Total_Damage_Inflation_Adjusted_Year": "Mention the year used for inflation adjustment, if applicable. If the amount is not adjusted for inflation or this detail is not provided, assign 'NULL'."
- "Economic_Impact_with_annotation": "Directly quote portions of the text that substantiate your findings on the total economic loss or damage. This should directly quote the original text."
}}
If the "Total_Damage" is not "NULL" or "0", then, delve deeper to provide a detailed breakdown of economic damages by country. 
For the first instance in the "Specific_Instance_Per_Country_Economic_Damage" section for each country, provide a summary of the total economic damage within that country and the "Location_Damage" is the country name, 
followed by a breakdown into specific cities, towns, or regions where possible.
Organize this information in JSON format as follows:
- "Specific_Instance_Per_Country_Damage":[ {{
- "Country": "Name of the country.",
- "Location_Damage": "The specific place within the country where the economic impact occurred, including towns, cities, or regions."
- "Damage": "The amount of economic damage."
- "Damage_Units": "The currency of the economic damage, like USD, EUR. If not specified, assign 'NULL'."
- "Damage_Inflation_Adjusted": "Indicate 'Yes' if the damage amount has been adjusted for inflation; otherwise, 'No'."
- "Damage_Inflation_Adjusted_Year": "The year of inflation adjustment, if applicable. If not adjusted or not applicable, assign 'NULL'."
- "Impact_Assessment_with_annotation": "Include text from the original article that supports your findings on the economic impact amount and details for each specific instance. This should directly quote the original text."
  }}]
Ensure to capture all instances of economic loss or damage mentioned in the article, including direct and indirect causes, and organize them in the JSON format output.
'''
prompt_building_per_country = f'''
Based on the provided article, which includes the information box {info_box} and the full text {Whole_text} related to {Event_Name}, 
first, summarize the total number of buildings reported as damaged due to {Event_Name}, 
covering a wide range of building types such as houses, apartments, office buildings, retail stores, hotels, schools, hospitals, and more. 
Organize the extracted information in JSON format as follows:
- "Total_Summary_Building_Damage": {{
- "Total_Buildings_Damage": "Record the total number of buildings reported as damaged. If no specific information is available, please assign 'NULL'."
- "Total_Building_Damage_with_annotation": "Directly quote segments from the article that provide evidence or mention the extent of total building damages. 
This should include any details that substantiate the reported number of buildings damaged and directly quote the original text."
}}
If the "Total_Buildings_Damage" is not "NULL" or "0", then, delve deeper to provide a detailed breakdown of building damage by country, 
the first instance in the "Specific_Instance_Per_Country_Building_Damage" section for each country provides a summary of the total building damage within that country and the "Location_Building" is the country name, 
followed by a breakdown into specific cities, towns, or regions where possible. 
Organize this information in JSON format as follows:
- "Specific_Instance_Per_Country_Building_Damage":[ {{
- "Country": "Name of the country.",
- "Location_Building_Damage": "The specific place within the country where the building damage occurred, including towns, cities, or regions."
- "Start_Date_Building_Damage": "The start date when the building damage occurred, if mentioned."
- "End_Date_Building_Damage": "The end date when the building damage occurred, if mentioned."
- "Building_Damage": "Record the number of buildings reported as damaged in the specific instance. In cases where no specific information is available, please assign 'NULL'."
- "Building_Damage_with_annotation": "Directly quote segments from the article that provide evidence or mention of building damages in the specific instance. This should include any details that substantiate your reported number of buildings damaged and directly quote the original text."
    }}]

Ensure to capture all instances of building damage mentioned in the article, including direct and indirect causes, and organize them in the JSON format output.
'''


event_results={"Event_Name":Event_Name,"Source":Source}
prompt_list_basic =[prompt_main_event,prompt_perils,prompt_location, prompt_time] # test if the location prompt works 
prompt_list_impact=[prompt_death_per_country,prompt_injuries_per_country,
             prompt_displaced_per_country,prompt_homeless_per_country,prompt_affected_per_country
             ,prompt_insure_per_country,prompt_total_per_country,
             prompt_building_per_country]

for prompt in prompt_list_basic:
    answer_str = completion_4(prompt)  # This returns a JSON string or string ( limitation of GPT3.5)
    answer_dict = json.loads(answer_str)  # Convert the JSON string to a Python dictionary
    event_results={"Prompt":prompt}
    event_results.update(answer_dict)
    response_wiki_GPT4.append(event_results)
# Iterate over each prompt in the prompt_list
for prompt in prompt_list_impact:
    answer_str = completion_4(prompt)  # This returns a JSON string or string ( limitation of GPT3.5)
    answer_dict = json.loads(answer_str)  # Convert the JSON string to a Python dictionary
    event_results={"Prompt":prompt}
    event_results.update(answer_dict)
    response_wiki_GPT4.append(event_results)

end_time = time.time()
# Calculate the total time taken and add it to the list
execution_time = end_time - start_time
#event_results["execution_time"]=execution_time
#response_wiki_GPT4.append(event_results)      

execution_times.append(execution_time)  


# Saving the results for all events to a JSON file
with open(Result_DIR+'response_wiki_GPT4_20240604_2021EuFloods.json', 'w') as json_file:
     json.dump(response_wiki_GPT4, json_file, indent=4)

# due to the limitation of GPT3.5, so the long article over 16385 tokens will be skip, which is also the multiple events article