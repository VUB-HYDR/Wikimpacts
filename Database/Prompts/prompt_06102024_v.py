response_gpt4o = []
for item in dev_json:
    Event_ID = str(item.get("Event_ID"))
    Source = str(item.get("Source"))
    Event_Name = str(item.get("Event_Name"))
    info_box = str(item.get("Info_Box"))
    Whole_text = ""
    if (
        Source != "https://en.wikipedia.org/wiki/2022_Dallas_floods"
    ):  # multi event article, just notice to correctly handle this
        whole_text_dict = item.get("Whole_Text")
        Whole_text = "".join(f"{key}: {value} " for key, value in whole_text_dict.items())
    else:
        Whole_text = item.get("Whole_Text").get("August 21\u201322[edit]")
    prompt_main_event_0610 = f"""Based on the provided article {info_box} {Whole_text}, please extract information about the main event {Event_Name} , and assign the details in JSON format as follows:
                - "Main_Event": "identify the event category referring to "Flood; Extratropical Storm/Cyclone; Tropical Storm/Cyclone; Extreme Temperature;
                  Drought; Wildfire; Tornado". Only one category should be assigned."
                - "Main_Event_Assessment_With_Annotation": "Include text from the original text that supports your findings on the Main_Event."
                Please make sure that your annotation text is explicitly from the original text provided. Only Give Json output, no extra explanation needed."""

    prompt_perils_0610 = f"""Based on the provided article {info_box} {Whole_text}, please extract information about the perils {Event_Name} , and assign the details in JSON format as follows:
        - "Perils": "identify the perils referring to "Wind; Rainfall; Flood; Landfall; Landslide; Blizzard; Hail; Lightning; Thunderstorm; Heatwave; Cold Spell/Cold Snap; Drought; Wildfire".
        If more than one peril is detected from the text, separate them with "|". "
        - "Perils_Assessment_With_Annotation": "Include text from the original text that supports your findings on the perils. "
         Ensure to capture all perils mentioned, and please make sure that your annotation text is explicitly from the original text provided. Only Give Json output, no extra explanation needed. """

    prompt_location_0610 = f"""
        Based on the provided article {info_box} {Whole_text}, identify all locations affected by {Event_Name} and assign the appropriate details in JSON format as follows.
        - "Location": "All places mentioned in the text as being affected by {Event_Name} in a list like ["location1";"location2"]."
        - "Location_with_Annotation": "For each location listed, include a snippet from the article that supports why you consider it affected by  {Event_Name} . This annotation should help illustrate how you determined the location was impacted. This should directly quote the original text."
         Ensure to capture all locations affected, and please make sure that your annotation text is explicitly from the original text provided. Only Give Json output, no extra explanation needed."""

    prompt_time_0610 = f"""
        Based on the provided article {info_box} {Whole_text}, identify the time infomation {Event_Name} described, and assign the appropriate details in JSON format as follows..
        - "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "Time_with_Annotation": "Include text from the original text that supports your findings on the start date and end date. This should directly quote the original text."
         Please make sure that your annotation text is explicitly from the original text provided. Only Give Json output, no extra explanation needed."""

    prompt_death_country_0610 = f"""Based on the provided article {info_box} {Whole_text}, extract the number of deaths associated with the {Event_Name}, along with supporting annotations from the article. The death information can be splited into 3 parts,
          the first is the total number of deaths caused by the {Event_Name}, and organize this information in JSON format as follows:
          - "Total_Summary_Death":{{
          - "Total_Deaths": "The total number of people who died in the {Event_Name}.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No death", "None", "None reported"). If the information is missing, assign 'NULL'."
          - "Total_Death_Annotation": "Provide excerpts from the article that directly support your findings on the total number of deaths. This should directly quote the original text."
          }}
          the second is the total number of deaths in each country caused by the {Event_Name}, and organize this information in JSON format as follows:
          - "Total_Death_Per_Country":[{{
          - "Country": "Name of the country."
          - "Start_Date_Death": "The start date when the deaths occurred, if mentioned."
          - "End_Date_Death":"The end date when the deaths occurred, if mentioned."
          - "Num_Death": "The total number of people who died in this country related to the {Event_Name}.
             Do not sum the number of deaths in specific locations within this country unless the article explicitly mentions a total number of deaths in this country.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No death", "None", "None reported"). If the information is missing or if no total number of death in this country is mentioned, assign 'NULL'."
          - "Death_with_annotation": "Excerpts from the article that support your findings on the location, time, number of deaths. This should directly quote the original text."
                }}]
          the third is the specific instance of deaths within each country caused by the {Event_Name}, make sure to capture all locations with death information and organize this information in JSON format as follows:
          - "Specific_Instance_Per_Country_Death":[{{
          - "Country": "Name of the country."
          - "Location_Death": "The specific place/places within the country where the deaths occurred, including towns, cities, or regions. Order it/them in a list like ["town";"city";"region"]."
          - "Start_Date_Death": "The start date when the deaths occurred, if mentioned."
          - "End_Date_Death":"The end date when the deaths occurred, if mentioned."
          - "Num_Death": "The number of people who died in the specific location/locations related to the {Event_Name}.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No death", "None", "None reported"). If the information is missing, assign 'NULL'."
          - "Death_with_annotation": "Excerpts from the article that support your findings on the location, time, number of deaths. This should directly quote the original text."
                }}]
          Ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """

    prompt_non_fatal_injury_country_0610 = f"""Based on the provided article {info_box} {Whole_text}, extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article. The non-fatal injuries information can be splited into 3 parts,
          the first is the total number of non-fatal injuries caused by the {Event_Name}, and organize this information in JSON format as follows:
          - "Total_Summary_Injury":{{
          - "Total_Injury": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in the {Event_Name}.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No injuries", "None", "None reported"). If the information is missing, assign 'NULL'."
          - "Total_Injury_Annotation": "Provide excerpts from the article that directly support your findings on the total number of non-fatal injuries. This should directly quote the original text."
          }}
          the second is the total number of non-fatal injuries in each country caused by the {Event_Name}, and organize this information in JSON format as follows:
          - "Total_Injury_Per_Country":[{{
          - "Country": "Name of the country."
          - "Start_Date_Injury": "The start date when the injuries occurred, if mentioned."
          - "End_Date_Injury":"The end date when the injuries occurred, if mentioned."
          - "Num_Injury": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in this country related to the {Event_Name}.
             Do not sum the number of injuries in specific locations within this country unless the article explicitly mentions a total number of injuries in this country.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No injuries", "None", "None reported"). If the information is missing or if no total number of injuries in this country is mentioned, assign 'NULL'."
          - "Injury_with_annotation": "Excerpts from the article that support your findings on the location, time, number of non-fatal injuries. This should directly quote the original text."
                }}]
          the third is the specific instance of non-fatal injuries within each country caused by the {Event_Name}, make sure to capture all locations with non-fatal injury information and organize this information in JSON format as follows:
          - "Specific_Instance_Per_Country_Injury":[{{
          - "Country": "Name of the country."
          - "Location_Injury": "The specific place/places within the country where the injuries occurred, including towns, cities, or regions. Order it/them in a list like ["town";"city";"region"]."
          - "Start_Date_Injury": "The start date when the injuries occurred, if mentioned."
          - "End_Date_Injury":"The end date when the injuries occurred, if mentioned."
          - "Num_Injury": "The number of people who got injured, hurt, wound, or hospitalized (excluding death) in the specific location/locations related to the {Event_Name}.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No injuries", "None", "None reported"). If the information is missing, assign 'NULL'."
          - "Injury_with_annotation": "Excerpts from the article that support your findings on the location, time, number of non-fatal injuries. This should directly quote the original text."
                }}]
          Ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    # updated prompts for displacement
    prompt_displacement_country_0610 = f"""Based on the provided article {info_box} {Whole_text}, extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article. The displacement information can be splited into 3 parts,
          the first is the total number of displacement caused by the {Event_Name}, and organize this information in JSON format as follows:
          - "Total_Summary_Displacement":{{
          - "Total_Displacement": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the {Event_Name}.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No displacement", "None", "None reported"). If the information is missing, assign 'NULL'."
          - "Total_Displacement_Annotation": "Provide excerpts from the article that directly support your findings on the total number of displacement. This should directly quote the original text."
          }}
          the second is the total number of displacement in each country caused by the {Event_Name}, and organize this information in JSON format as follows:
          - "Total_Displacement_Per_Country":[{{
          - "Country": "Name of the country."
          - "Start_Date_Displacement": "The start date when the displacement occurred, if mentioned."
          - "End_Date_Displacement":"The end date when the displacement occurred, if mentioned."
          - "Num_Displacement": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in this country related to the {Event_Name}.
             Do not sum the number of displacement in specific locations within this country unless the article explicitly mentions a total number of displacement in this country.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No displacement", "None", "None reported"). If the information is missing or if no total number of displacement in this country is mentioned, assign 'NULL'."
          - "Displacement_with_annotation": "Excerpts from the article that support your findings on the location, time, number of displacement. This should directly quote the original text."
                }}]
          the third is the specific instance of displacement within each country caused by the {Event_Name}, make sure to capture all locations with displacement information and organize this information in JSON format as follows:
          - "Specific_Instance_Per_Country_Displacement":[{{
          - "Country": "Name of the country."
          - "Location_Displacement": "The specific place/places within the country where the displacement occurred, including towns, cities, or regions. Order it/them in a list like ["town";"city";"region"]."
          - "Start_Date_Displacement": "The start date when the displacement occurred, if mentioned."
          - "End_Date_Displacement":"The end date when the displacement occurred, if mentioned."
          - "Num_Displacement": "The number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the specific location/locations related to the {Event_Name}.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No displacement", "None", "None reported"). If the information is missing, assign 'NULL'."
          - "Displacement_with_annotation": "Excerpts from the article that support your findings on the location, time, number of displacement. This should directly quote the original text."
                }}]
          Ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    # updated prompts for homelessness
    prompt_homelessness_country_0610 = f"""Based on the provided article {info_box} {Whole_text}, extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article. The homelessness information can be splited into 3 parts,
          the first is the total number of homelessness caused by the {Event_Name}, and organize this information in JSON format as follows:
          - "Total_Summary_Homelessness":{{
          - "Total_Homelessness": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, are unhoused, without shelter, houseless, or shelterless in the {Event_Name}.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No homelessness", "None", "None reported"). If the information is missing, assign 'NULL'."
          - "Total_Homelessness_Annotation": "Provide excerpts from the article that directly support your findings on the total number of homelessness. This should directly quote the original text."
          }}
          the second is the total number of homelessness in each country caused by the {Event_Name}, and organize this information in JSON format as follows:
          - "Total_Homelessness_Per_Country":[{{
          - "Country": "Name of the country."
          - "Start_Date_Homelessness": "The start date when the homelessness occurred, if mentioned."
          - "End_Date_Homelessness":"The end date when the homelessness occurred, if mentioned."
          - "Num_Homelessness": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, are unhoused, without shelter, houseless, or shelterless in this country related to the {Event_Name}.
             Do not sum the number of homelessness in specific locations within this country unless the article explicitly mentions a total number of homelessness in this country.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No homelessness", "None", "None reported"). If the information is missing or if no total number of homelessness in this country is mentioned, assign 'NULL'."
          - "Homelessness_with_annotation": "Excerpts from the article that support your findings on the location, time, number of homelessness. This should directly quote the original text."
                }}]
          the third is the specific instance of homelessness within each country caused by the {Event_Name}, make sure to capture all locations with homelessness information and organize this information in JSON format as follows:
          - "Specific_Instance_Per_Country_Homelessness":[{{
          - "Country": "Name of the country."
          - "Location_Homelessness": "The specific place/places within the country where the homelessness occurred, including towns, cities, or regions. Order it/them in a list like ["town";"city";"region"]."
          - "Start_Date_Homelessness": "The start date when the homelessness occurred, if mentioned."
          - "End_Date_Homelessness":"The end date when the homelessness occurred, if mentioned."
          - "Num_Homelessness": "The number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, are unhoused, without shelter, houseless, or shelterless in the specific location/locations related to the {Event_Name}.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No homelessness", "None", "None reported"). If the information is missing, assign 'NULL'."
          - "Homelessness_with_annotation": "Excerpts from the article that support your findings on the location, time, number of homelessness. This should directly quote the original text."
                }}]
          Ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    # updated prompts for affected
    prompt_affected_country_0610 = f"""Based on the provided article {info_box} {Whole_text}, extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article. The number of affected people information can be splited into 3 parts,
          the first is the total number of affected people caused by the {Event_Name}, and organize this information in JSON format as follows:
          - "Total_Summary_Affected":{{
          - "Total_Affected": "The total number of people who were affected, impacted, or influenced in the {Event_Name}.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No affected people', 'None', 'None reported'). If the information is missing, assign 'NULL'."
          - "Total_Affected_Annotation": "Provide excerpts from the article that directly support your findings on the total number of affected people. This should directly quote the original text."
          }}
          the second is the total number of affected people in each country caused by the {Event_Name}, and organize this information in JSON format as follows:
          - "Total_Affected_Per_Country":[{{
          - "Country": "Name of the country."
          - "Start_Date_Affected": "The start date when the affected people occurred, if mentioned."
          - "End_Date_Affected":"The end date when the affected people occurred, if mentioned."
          - "Num_Affected": "The total number of people who were affected, impacted, or influenced in this country related to the {Event_Name}.
             Do not sum the number of affected people in specific locations within this country unless the article explicitly mentions a total number of affected people in this country.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No affected people", "None", "None reported"). If the information is missing or if no total number of affected people in this country is mentioned, assign 'NULL'."
          - "Affected_with_annotation": "Excerpts from the article that support your findings on the location, time, number of affected people. This should directly quote the original text."
                }}]
          the third is the specific instance of affected people within each country caused by the {Event_Name}, make sure to capture all locations with affected people information and organize this information in JSON format as follows:
          - "Specific_Instance_Per_Country_Affected":[{{
          - "Country": "Name of the country."
          - "Location_Affected": "The specific place/places within the country where the affected people occurred, including towns, cities, or regions. Order it/them in a list like ["town";"city";"region"]."
          - "Start_Date_Affected": "The start date when the affected people occurred, if mentioned."
          - "End_Date_Affected":"The end date when the affected people occurred, if mentioned."
          - "Num_Affected": "The number of people who were affected, impacted, or influenced in the specific location/locations related to the {Event_Name}.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands of,' '300-500 people', 'No affected people", "None", "None reported"). If the information is missing, assign 'NULL'."
          - "Affected_with_annotation": "Excerpts from the article that support your findings on the location, time, number of affected people. This should directly quote the original text."
                }}]
          Ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """

    # updated prompts for insured damage
    prompt_insure_per_country_0610 = f"""
        Based on the provided article, which includes the information box {info_box} and the full text {Whole_text} related to {Event_Name}, extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article. The insured damage information can be splited into 3 parts,
        the first is the total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy, and organize this information in JSON format as follows:
        - "Total_Summary_Insured_Damage": {{
        - "Total_Insured_Damage": "The total amount of insured damage. Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
        - "Total_Insured_Damage_Units": "The currency of the total insured damage, like USD, EUR. If not specified, assign 'NULL'."
        - "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise, 'No'."
        - "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable. If not adjusted or not applicable, assign 'NULL'."
        - "Total_Insured_Damage_Assessment_with_annotation": "Provide excerpts from the article that support your findings on the total amount of insured damage. This should directly quote the original text."
        }}
        the second is the total insured damage in each country caused by the {Event_Name}, and organize this information in JSON format as follows:
         - "Total_Insured_Damage_Per_Country":[{{
          - "Country": "Name of the country."
          - "Total_Insured_Damage": "The total amount of insured damage in this country related to the {Event_Name}. Do not sum the insured damage in specific locations within this country unless the article explicitly mentions a total insured damage in this country.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing or if no total insured damage in this country is mentioned, assign 'NULL'."
          - "Total_Insured_Damage_Units": "The currency of the total insured damage, like USD, EUR. If not specified, assign 'NULL'."
          - "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise, 'No'."
          - "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable. If not adjusted or not applicable, assign 'NULL'."
          - "Total_Insured_Damage_Assessment_with_annotation": "Provide excerpts from the article that support your findings on the total amount of insured damage. This should directly quote the original text."
                }}]
        the third is the specific instance of insured damage within each country caused by the {Event_Name}, make sure to capture all locations with insured damage information and organize this information in JSON format as follows:
          - "Specific_Instance_Per_Country_Insured_Damage":[{{
          - "Country": "Name of the country."
          - "Location_Insured_Damage": "The specific place/places within the country where the insured damage occurred, including towns, cities, or regions. Order it/them in a list like ["town";"city";"region"]."
          - "Num_Insured_Damage": "The amount of insured damage in the specific location/locations related to the {Event_Name}.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
          - "Insured_Damage_Units": "The currency of the insured damage, like USD, EUR. If not specified, assign 'NULL'."
          - "Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the insured damage amount has been adjusted for inflation; otherwise, 'No'."
          - "Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the insured damage, if applicable. If not adjusted or not applicable, assign 'NULL'."
          - "Insured_Damage_Assessment_with_annotation": "Provide excerpts from the article that support your findings on the amount of insured damage. This should directly quote the original text."

             }}]
        Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes, and organize them in the JSON format output. Only Give Json output, no extra explanation needed. """

    # updated prompts for total damage
    prompt_total_damage_per_country_0610 = f"""
        Based on the provided article, which includes the information box {info_box} and the full text {Whole_text} related to {Event_Name}, extract the total economic loss or damage information associated with the {Event_Name}, along with supporting annotations from the article. The total economic loss or damage  information can be splited into 3 parts,
        the first is the total economic loss or damage caused by the {Event_Name}, and organize this information in JSON format as follows:
        - "Total_Summary_Damage": {{
        - "Total_Economic_Damage": "The total amount of economic loss or damage. Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
        - "Total_Economic_Damage_Units": "The currency of the total economic loss or damage, like USD, EUR. If not specified, assign 'NULL'."
        - "Total_Economic_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total economic loss or damage amount has been adjusted for inflation; otherwise, 'No'."
        - "Total_Economic_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic loss or damage, if applicable. If not adjusted or not applicable, assign 'NULL'."
        - "Total_Economic_Damage_Assessment_with_annotation": "Provide excerpts from the article that support your findings on the total amount of economic loss or damage. This should directly quote the original text."
        }}
        the second is the total economic loss or damage in each country caused by the {Event_Name}, and organize this information in JSON format as follows:
         - "Total_Economic_Damage_Per_Country":[{{
          - "Country": "Name of the country."
          - "Total_Economic_Damage": "The total amount of economic loss or damage in this country related to the {Event_Name}. Do not sum the total economic damage in specific locations within this country unless the article explicitly mentions a total economic damage in this country.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing or if no total economic damage in this country is mentioned, assign 'NULL'."
          - "Total_Economic_Damage_Units": "The currency of the total economic damage, like USD, EUR. If not specified, assign 'NULL'."
          - "Total_Economic_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise, 'No'."
          - "Total_Economic_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable. If not adjusted or not applicable, assign 'NULL'."
          - "Total_Economic_Damage_Assessment_with_annotation": "Provide excerpts from the article that support your findings on the total amount of economic damage. This should directly quote the original text."
                }}]
        the third is the specific instance of economic damage within each country caused by the {Event_Name}, make sure to capture all locations with economic damage information and organize this information in JSON format as follows:
          - "Specific_Instance_Per_Country_Economic_Damage":[{{
          - "Country": "Name of the country."
          - "Location_Economic_Damage": "The specific place/places within the country where the economic damage occurred, including towns, cities, or regions. Order it/them in a list like ["town";"city";"region"]."
          - "Num_Economic_Damage": "The amount of economic damage in the specific location/locations related to the {Event_Name}.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
          - "Economic_Damage_Units": "The currency of the economic damage, like USD, EUR. If not specified, assign 'NULL'."
          - "Economic_Damage_Inflation_Adjusted": "Indicate 'Yes' if the economic damage amount has been adjusted for inflation; otherwise, 'No'."
          - "Economic_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the economic damage, if applicable. If not adjusted or not applicable, assign 'NULL'."
          - "Economic_Damage_Assessment_with_annotation": "Provide excerpts from the article that support your findings on the amount of economic damage. This should directly quote the original text."
             }}]
        Ensure to capture all instances of economic loss or damage mentioned in the article, including direct and indirect cause. Only Give Json output, no extra explanation needed. """

    prompt_building_damage_country_0610 = f"""Based on the provided article {info_box} {Whole_text}, extract the number of damaged buildings associated with the {Event_Name}, covering a wide range of building types such as homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more, along with supporting annotations from the article. The number of damaged buildings information can be splited into 3 parts,
      the first is the total number of damaged buildings caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Building_Damage":{{
      - "Total_Building_Damage": "The total number of damaged buildings in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few", "several", "None", "None reported"). If the information is missing, assign 'NULL'."
      - "Total_Building_Damage_Annotation": "Provide excerpts from the article that directly support your findings on the total number of damaged buildings. This should directly quote the original text."
      }}
      the second is the total number of damaged buildings in each country caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Building_Damage_Per_Country":[{{
      - "Country": "Name of the country."
      - "Start_Date_Building_Damage": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date_Building_Damage":"The end date when the damaged buildings occurred, if mentioned."
      - "Num_Building_Damage": ""The total number of damaged buildings in this country related to the {Event_Name}.
         Do not sum the number of damaged buildings in specific locations within this country unless the article explicitly mentions a total number of damaged buildings in this country.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few", "several", "None", "None reported"). If the information is missing or if no total number of damaged buildings in this country is mentioned, assign 'NULL'."
      - "Building_Damage_with_annotation": "Excerpts from the article that support your findings on the location, time, total number of damaged buildings. This should directly quote the original text."
            }}]
      the third is the specific instance of damaged buildings within each country caused by the {Event_Name}, make sure to capture all locations with damaged buildings information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Country_Building_Damage":[{{
      - "Country": "Name of the country."
      - "Location_Building_Damage": "The specific place/places within the country where the damaged buildings occurred, including towns, cities, or regions. Order it/them in a list like ["town";"city";"region"]."
      - "Start_Date_Building_Damage": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date_Building_Damage":"The end date when the damaged buildings occurred, if mentioned."
      - "Num_Building_Damage": "The number of damaged buildings in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few", "several", "None", "None reported"). If the information is missing, assign 'NULL'."
      - "Building_Damage_with_annotation": "Excerpts from the article that support your findings on the location, time, number of damaged buildings. This should directly quote the original text."
            }}]
      Ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
