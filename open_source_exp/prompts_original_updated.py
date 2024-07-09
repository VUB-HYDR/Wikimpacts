prompt_main_event = '''Based on the provided article {info_box} {Whole_text}, please extract information about the main event {Event_Name} , and assign the details as follows:
    - "Main_Event": "identify the event category referring to "Flood; Extratropical Storm/Cyclone; Tropical Storm/Cyclone; Extreme Temperature;
      Drought; Wildfire; Tornado". Only one category should be assigned."
    - "Main_Event_Assessment_With_Annotation": "Include text from the original text that supports your findings on the Main_Event."
    please give the json format output of these two items above, and please make sure that your annotation text is explicitly from the original text provided.
    Please produce the response strictly in JSON format. Ensure the JSON is correctly formatted, closely following the described field names, without any extra text, comments, or explanations outside the JSON structure.
    JSON files can only consist of these two key names: "Main_Event", "Main_Event_Assessment_With_Annotation". Do not include any other key names or extra text.

    '''

prompt_country = '''                                                                                                                                     
    Based on the provided article {info_box} {Whole_text}, identify all countries affected by {Event_Name} 
    and assign the appropriate details. 
     {{
    "Country": "List all countries mentioned in the text as being affected by  {Event_Name}."
    "Country_with_Annotation": "For each location listed, include a snippet from the article that supports why you consider it affected by {Event_Name}. This annotation should help illustrate how you determined the country was impacted. This should directly quote the original text."
     }}
    please give the json format output of these two items above, and please make sure that your annotation text is explicitly from the original text provided.
    Please produce the response strictly in JSON format. Ensure the JSON is correctly formatted, closely following the described field names, without any extra text, comments, or explanations outside the JSON structure.
    JSON files can only consist of these two key names: "Country", "Country_with_Annotation". Do not include any other key names or extra text.
    '''

prompt_time = '''
    Based on the provided article {info_box} {Whole_text}, identify the time infomation {Event_Name} described, and assign the appropriate details.
    Please provide the output strictly in the following JSON format, with the exact field names and structure:
        {{    
            "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned.",
            "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned.",
            "Time_with_Annotation": "Include text from the original text that supports your findings on the start date and end date. This should directly quote the original text.",
        }}
    Please give the json format output of these three items above, and please make sure that your annotation text is explicitly from the original text provided.
    Please produce the response strictly in JSON format. Ensure the JSON is correctly formatted, closely following the described field names, without any extra text, comments, or explanations outside the JSON structure. 
    JSON files can only consist of these three key names: "Start_Date", "End_Date", and "Time_with_Annotation". Do not include any other key names or extra text.
    '''

prompt_death_per_country = '''
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
    Please produce the response strictly in JSON format. Ensure the JSON is correctly formatted, closely following the described field names, without any extra text, comments, or explanations outside the JSON structure.
'''

prompt_total_per_country = '''
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
        - "Damage_Assessment_with_annotation": "Include text from the original article that supports your findings on the economic impact amount and details for each specific instance. This should directly quote the original text."
          }}]
        Ensure to capture all instances of economic loss or damage mentioned in the article, including direct and indirect causes, and organize them in the JSON format output.
        Please produce the response strictly in JSON format. Ensure the JSON is correctly formatted, closely following the described field names, without any extra text, comments, or explanations outside the JSON structure.
        '''

prompts_original_dictionary_updated = {
    "prompt_main_event": prompt_main_event,
    "prompt_country": prompt_country,
    "prompt_time": prompt_time,
    "prompt_death_per_country": prompt_death_per_country,
    "prompt_damage_per_country": prompt_total_per_country
}