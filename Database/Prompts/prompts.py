# V_0 is a list of prompts used in the NLP2024 paper
# V_1 is the list of prompts used for L1-3 and the annotation is directly quoted from the article finalized in 20240610
# V_2 is the list of prompts for L1-3 with annotation gives the header names, finalized in 20240715
# V_3_1 is a version based on V2, but with freezed variable names as the schema we confirmed, 20240823
# V_3_2 is the version based on V3, but in L1, only prompt the model to capture countries, and we use this as the final version for test and full run
# V_3_3 is the version based on V3_2, but the infobox and the whole text are feed in the end of the prompt.
# V_4 is the one with two prompts for each impact category, one prompt for L1/2 and one for L3
# V_5 is the one with three prompts for each impact category
# V_6 is a version based on V3 but force the model not to generate null for non-nullable items, and also for the L1 only ask for country information
# V_3_Country is the version that only run prompt to extract the country in L1


# Wikimpacts V2 prompt design
# V_7 is the first version of wikimpacts V2 prompts, based on Version 1.0 Wikimpacts database, we  


V_0: dict = {
    "deaths": [
        """Based on the provided article, which includes the information
    box {Info_Box} and the full text {Whole_Text}, first extract
    and summarize the total number of deaths associated with
    {Event_Name}, along with supporting annotations from the article.
    Organize this information in JSON format as follows:

    - "Total_Summary_Death":{{
    - "Total_Deaths": "The total number of people who died in
    {Event_Name}, both directly and indirectly.
    Use the exact number if mentioned, or retain the text or range as
    provided for vague numbers (e.g., 'hundreds of,' '500 families,'
    'thousands of,' '300-500 people'). If the information is missing,
    assign 'NULL'."
    - "Total_Death_Annotation": "Provide excerpts from the article
    that directly support your findings on the total number of
    deaths. This should directly quote the original text."
    }}

    If the "Total_Deaths" is not "NULL" or "0", then, delve deeper to
    provide a detailed breakdown of these deaths by country.
    The first instance in the "Specific_Instance_Per_Country_Death"
    section for each country provides a summary of the total deaths
    within that country and the "Location_Death" is the country name,
    followed by a breakdown into specific cities, towns, or regions
    where possible. Organize this information in JSON format as follows:

    - "Specific_Instance_Per_Country_Death":[{{
    - "Country": "Name of the country."
    - "Location_Death": "The specific place within the country where
    the deaths occurred, including towns, cities, or regions."
    - "Start_Date_Death": "The start date when the deaths occurred,
    if mentioned."
    - "End_Date_Death":"The end date when the deaths occurred, if
    mentioned."
    - "Num_Death": "The number of people who died in this specific
    location or incident related to {Event_Name}. Use the exact
    number if mentioned, or retain the text or range as provided for
    vague numbers (e.g., 'hundreds of,' '500 families,' 'thousands
    of,' '300-500 people'). If the information is missing, assign
    'NULL'."
    - "Death_with_annotation": "Excerpts from the article that
    support your findings on the location, time, number of deaths.
    This should directly quote the original text."
    }}]

    Ensure to capture all instances of death mentioned in the
    article, including direct and indirect causes. """
    ],
    "Main_Event": [
        """ Based on the provided article {Info_Box} {Whole_Text},
        please extract information about the main event {Event_Name},
        and assign the details as follows:

        - "Main_Event": "identify the event category referring to
        "Flood; Extratropical Storm/Cyclone; Tropical Storm/Cyclone; Extreme
        Temperature; Drought; Wildfire; Tornado".
        Only one category should be assigned."

        - "Main_Event_Assessment_With_Annotation": "Include text from
        the original text that supports your findings on the Main_Event."
        please give the json format output of these two items above,
        and please make sure that your annotation text is explicitly
        from the original text provided."""
    ],
    "Time": [
        """   Based on the provided article {Info_Box} {Whole_Text},
    identify the time infomation {Event_Name} described,
    and assign the appropriate details:

    - "Start_Date": "The start date of the event. If the specific
    day or month is not known, include at least the year if it's
    available. If no time information is available, enter 'NULL'.
    If the exact date is not clear (e.g., "summer of 2021", "June
    2020"), please retain the text as mentioned."

    - "End_Date": "The end date of the event. If the specific day or
    month is not known, include at least the year if it's available.
    If no time information is available, enter 'NULL'. If the exact
    date is not clear (e.g., "summer of 2021", "June 2020"), please
    retain the text as mentioned."

    - "Time_With_Annotation": "Include text from the original text
    that supports your findings on the start date and end date.
    This should directly quote the original text."

    Please give the json format output of these three items above,
    and please make sure that your annotation text is explicitly
    from the original text provided."""
    ],
    "Country": [
        """  Based on the provided article {Info_Box} {Whole_Text},
    identify all countries affected by {Event_Name},
    and assign the appropriate details:

    - "Country": "List all countries mentioned in the text as being
    affected by {Event_Name}."

    - "Country_With_Annotation": "For each location listed, include
    a snippet from the article that supports why you consider it
    affected by {Event_Name}. This annotation should help illustrate
    how you determined the country was impacted. This should directly
    quote the original text."

    Please give the json format output of these two items above,
    and please make sure that your annotation text is explicitly
    from the original text provided."""
    ],
    "damage": [
        """ Based on the provided article, which includes the information
    box {Info_Box} and the full text {Whole_Text} related to
    {Event_Name}, first extract and summarize detailed information
    about the total economic loss or damage caused by {Event_Name},
    focusing specifically on the economic impact in the mentioned
    regions. The information should be organized in JSON format
    as follows:

    - "Total_Summary_Damage": {{
    - "Total_Damage": "Specify the economic loss or damage reported.
    If this information is not mentioned, assign 'NULL'."
    - "Total_Damage_Unit": "Indicate the currency of the reported damage
    (e.g., USD, EUR). If the currency is not specified, assign 'NULL'."
    - "Total_Damage_Inflation_Adjusted": "State 'Yes' if the reported
    damage amount has been adjusted for inflation; otherwise, indicate
    'No'. If this aspect is not mentioned, provide your best judgment
    based on the context."
    - "Total_Damage_Inflation_Adjusted_Year": "Mention the year used for
    inflation adjustment, if applicable. If the amount is not adjusted
    for inflation or this detail is not provided, assign 'NULL'."
    - "Economic_Impact_with_annotation": "Directly quote portions of
    the text that substantiate your findings on the total economic loss
    or damage. This should directly quote the original text."
    }}

    If the "Total_Damage" is not "NULL" or "0", then, delve deeper
    to provide a detailed breakdown of economic damages by country.
    For the first instance in the
    "Specific_Instance_Per_Country_Economic_Damage" section for each
    country, provide a summary of the total economic damage within that country
    and the "Location_Damage" is the country name,
    followed by a breakdown into specific cities, towns, or regions
    where possible. Organize this information in JSON format as follows:
    - "Specific_Instance_Per_Country_Damage":[ {{
    - "Country": "Name of the country.",
    - "Location_Damage": "The specific place within the country where the
    economic impact occurred, including towns, cities, or regions."
    - "Damage": "The amount of economic damage."
    - "Damage_Unit": "The currency of the economic damage, like USD, EUR.
    If not specified, assign 'NULL'."
    - "Damage_Inflation_Adjusted": "Indicate 'Yes' if the damage amount
    has been adjusted for inflation; otherwise, 'No'."
    - "Damage_Inflation_Adjusted_Year": "The year of inflation adjustment,
    if applicable. If not adjusted or not applicable, assign 'NULL'."
    - "Damage_Assessment_with_annotation": "Include text from the original
    article that supports your findings on the economic impact amount and
    details for each specific instance. This should directly quote the
    original text."
    }}]

    Ensure to capture all instances of economic loss or damage mentioned
    in the article, including direct and indirect causes, and organize
    them in the JSON format output."""
    ],
}

# V_1 is the list of prompts used for L1-3 and the annotation is directly quoted from the article finalized in 20240610
V_1: dict = {
    "main_event": [
        """Based on the provided article {Info_Box} {Whole_Text}, please extract information about the main event {Event_Name} , and assign the details in JSON format as follows:
                - "Main_Event": "identify the event category referring to "Flood; Extratropical Storm/Cyclone; Tropical Storm/Cyclone; Extreme Temperature;
                  Drought; Wildfire; Tornado". Only one category should be assigned."
                - "Main_Event_Assessment_With_Annotation": "Include text from the original text that supports your findings on the Main_Event."
                Please make sure that your annotation text is explicitly from the original text provided. Only Give Json output, no extra explanation needed."""
    ],
    "perils": [
        """Based on the provided article {Info_Box} {Whole_Text}, please extract information about the perils {Event_Name} , and assign the details in JSON format as follows:
        - "Perils": "identify the perils referring to "Wind; Rainfall; Flood; Landfall; Landslide; Blizzard; Hail; Lightning; Thunderstorm; Heatwave; Cold Spell/Cold Snap; Drought; Wildfire".
        If more than one peril is detected from the text, separate them with "|". "
        - "Perils_Assessment_With_Annotation": "Include text from the original text that supports your findings on the perils. "
         Ensure to capture all perils mentioned, and please make sure that your annotation text is explicitly from the original text provided. Only Give Json output, no extra explanation needed. """
    ],
    "location": [
        """
        Based on the provided article {Info_Box} {Whole_Text}, identify all locations affected by {Event_Name} and assign the appropriate details in JSON format as follows.
        - "Location": "All places mentioned in the text as being affected by {Event_Name} in a list like ["location1";"location2"]."
        - "Location_with_Annotation": "For each location listed, include a snippet from the article that supports why you consider it affected by  {Event_Name} . This annotation should help illustrate how you determined the location was impacted. This should directly quote the original text."
         Ensure to capture all locations affected, and please make sure that your annotation text is explicitly from the original text provided. Only Give Json output, no extra explanation needed."""
    ],
    "time": [
        """
        Based on the provided article {Info_Box} {Whole_Text}, identify the time infomation {Event_Name} described, and assign the appropriate details in JSON format as follows..
        - "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "Time_with_Annotation": "Include text from the original text that supports your findings on the start date and end date. This should directly quote the original text."
         Please make sure that your annotation text is explicitly from the original text provided. Only Give Json output, no extra explanation needed."""
    ],
    "deaths": [
        """Based on the provided article {Info_Box} {Whole_Text}, extract the number of deaths associated with the {Event_Name}, along with supporting annotations from the article. The death information can be splited into 3 parts,
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
    ],
    "injuries": [
        """Based on the provided article {Info_Box} {Whole_Text}, extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article. The non-fatal injuries information can be splited into 3 parts,
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
    ],
    "displaced": [
        """Based on the provided article {Info_Box} {Whole_Text}, extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article. The displacement information can be splited into 3 parts,
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
    ],
    "homeless": [
        """Based on the provided article {Info_Box} {Whole_Text}, extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article. The homelessness information can be splited into 3 parts,
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
    ],
    "affected": [
        """Based on the provided article {Info_Box} {Whole_Text}, extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article. The number of affected people information can be splited into 3 parts,
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
    ],
    "insured_damage": [
        """
        Based on the provided article, which includes the information box {Info_Box} and the full text {Whole_Text} related to {Event_Name}, extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article. The insured damage information can be splited into 3 parts,
        the first is the total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy, and organize this information in JSON format as follows:
        - "Total_Summary_Insured_Damage": {{
        - "Total_Insured_Damage": "The total amount of insured damage. Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
        - "Total_Insured_Damage_Unit": "The currency of the total insured damage, like USD, EUR. If not specified, assign 'NULL'."
        - "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise, 'No'."
        - "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable. If not adjusted or not applicable, assign 'NULL'."
        - "Total_Insured_Damage_Assessment_with_annotation": "Provide excerpts from the article that support your findings on the total amount of insured damage. This should directly quote the original text."
        }}
        the second is the total insured damage in each country caused by the {Event_Name}, and organize this information in JSON format as follows:
         - "Total_Insured_Damage_Per_Country":[{{
          - "Country": "Name of the country."
          - "Total_Insured_Damage": "The total amount of insured damage in this country related to the {Event_Name}. Do not sum the insured damage in specific locations within this country unless the article explicitly mentions a total insured damage in this country.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing or if no total insured damage in this country is mentioned, assign 'NULL'."
          - "Total_Insured_Damage_Unit": "The currency of the total insured damage, like USD, EUR. If not specified, assign 'NULL'."
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
          - "Insured_Damage_Unit": "The currency of the insured damage, like USD, EUR. If not specified, assign 'NULL'."
          - "Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the insured damage amount has been adjusted for inflation; otherwise, 'No'."
          - "Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the insured damage, if applicable. If not adjusted or not applicable, assign 'NULL'."
          - "Insured_Damage_Assessment_with_annotation": "Provide excerpts from the article that support your findings on the amount of insured damage. This should directly quote the original text."

             }}]
        Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes, and organize them in the JSON format output. Only Give Json output, no extra explanation needed. """
    ],
    "damage": [
        """
        Based on the provided article, which includes the information box {Info_Box} and the full text {Whole_Text} related to {Event_Name}, extract the total economic loss or damage information associated with the {Event_Name}, along with supporting annotations from the article. The total economic loss or damage  information can be splited into 3 parts,
        the first is the total economic loss or damage caused by the {Event_Name}, and organize this information in JSON format as follows:
        - "Total_Summary_Damage": {{
        - "Total_Economic_Damage": "The total amount of economic loss or damage. Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
        - "Total_Economic_Damage_Unit": "The currency of the total economic loss or damage, like USD, EUR. If not specified, assign 'NULL'."
        - "Total_Economic_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total economic loss or damage amount has been adjusted for inflation; otherwise, 'No'."
        - "Total_Economic_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic loss or damage, if applicable. If not adjusted or not applicable, assign 'NULL'."
        - "Total_Economic_Damage_Assessment_with_annotation": "Provide excerpts from the article that support your findings on the total amount of economic loss or damage. This should directly quote the original text."
        }}
        the second is the total economic loss or damage in each country caused by the {Event_Name}, and organize this information in JSON format as follows:
         - "Total_Economic_Damage_Per_Country":[{{
          - "Country": "Name of the country."
          - "Total_Economic_Damage": "The total amount of economic loss or damage in this country related to the {Event_Name}. Do not sum the total economic damage in specific locations within this country unless the article explicitly mentions a total economic damage in this country.
             Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing or if no total economic damage in this country is mentioned, assign 'NULL'."
          - "Total_Economic_Damage_Unit": "The currency of the total economic damage, like USD, EUR. If not specified, assign 'NULL'."
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
          - "Economic_Damage_Unit": "The currency of the economic damage, like USD, EUR. If not specified, assign 'NULL'."
          - "Economic_Damage_Inflation_Adjusted": "Indicate 'Yes' if the economic damage amount has been adjusted for inflation; otherwise, 'No'."
          - "Economic_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the economic damage, if applicable. If not adjusted or not applicable, assign 'NULL'."
          - "Economic_Damage_Assessment_with_annotation": "Provide excerpts from the article that support your findings on the amount of economic damage. This should directly quote the original text."
             }}]
        Ensure to capture all instances of economic loss or damage mentioned in the article, including direct and indirect cause. Only Give Json output, no extra explanation needed. """
    ],
    "damaged_buildings": [
        """Based on the provided article {Info_Box} {Whole_Text}, extract the number of damaged buildings associated with the {Event_Name}, covering a wide range of building types such as homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more, along with supporting annotations from the article. The number of damaged buildings information can be splited into 3 parts,
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
    ],
}

# V_2 is the list of prompts for L1-3 with annotation gives the header names, finalized in 20240715
V_2: dict = {
    "affected": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
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
    ],
    "damaged_buildings": [
        """Based on the provided article {Info_Box} {Whole_Text},
      extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting annotations from the article. The number of damaged buildings information can be splited into 3 parts,
      the first is the total number of damaged buildings caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Building_Damage":{{
      - "Total_Building_Damage": "The total number of damaged buildings in the {Event_Name}.
          Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
          Do not sum the number of damaged buildings in the article to present the total number of damaged buildings,
          and if no total number of damaged buildings explicitly mentioned or the information is missing, assign 'NULL'."
      - "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total number of damaged buildings. The output should only include "Info_Box" or the header name."
        }}
      the second is the total number of damaged buildings in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Building_Damage_Per_Country":[{{
      - "Country": "Name of the country where the building damage occured, and no matter the building damage is in one or several countries, please order them in a list like [Country1, Country2, Country3].."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": ""The total number of damaged buildings in this level related to the {Event_Name}.
         Do not sum the number of damaged buildings in specific locations from the country to present the total number of damaged buildings for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
         If the information is missing or if no total number of damaged buildings in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total building damage in this level. The output should only include the header name."
            }}]
      the third is the specific instance of damaged buildings within each country caused by the {Event_Name}, make sure to capture all locations with damaged buildings information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Country_Building_Damage":[{{
      - "Country": "Name of the country."
      - "Location": "The specific place/places within the country where the damaged buildings occurred, and no matter the building damage is in one or several places, order it/them in a list like ["city1";"city2";"city3"]."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": "The number of damaged buildings in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes"). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the building damage in this location. The output should only include the header name."
            }}]
      Ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "deaths": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract the number of deaths associated with the {Event_Name},
      along with supporting annotations from the article. The death information can be splited into 3 parts,
      the first is the total number of deaths caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Death":{{
      - "Total_Death": "The total number of people who died in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of death in the article to present the total number of death, and if no total number of death explicitly mentioned or the information is missing, assign 'NULL'."
      - "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total death. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of deaths in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Death_Per_Country":[{{
      - "Country": "Name of the country where the death occurred, and no matter the deaths are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The total number of people who died in this level related to the {Event_Name}.
         Do not sum the number of death in specific locations from the country to present the total number of death for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of death in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total death in this level. The output should only include the header name."
            }}]
      the third is the specific instance of deaths in the sub-national level caused by the {Event_Name}, make sure to capture all locations with death information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Country_Death":[{{
      - "Country": "Name of the country."
      - "Location": "The specific place within the country where the deaths occurred, and no matter the deaths are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The number of people who died in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the death in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "displaced": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article.
      The displacement information can be splited into 3 parts,
      the first is the total number of displacement caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Displace":{{
      - "Total_Displace": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of displacement in the article to present the total number of displacement,
         and if no total number of displacement explicitly mentioned or the information is missing, assign 'NULL'."
      - "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total displacement. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of displacement in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Displace_Per_Country":[{{
      - "Country": "Name of the country where the displacement occurred, and no matter the displacement is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in this level related to the {Event_Name}.
         Do not sum the number of displacement in specific locations from the country to present the total number of displacement for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of displacement in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total displacement in this level. The output should only include the header name."
            }}]
      the third is the specific instance of displacement in the sub-national level caused by the {Event_Name}, make sure to capture all locations with displacement information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Country_Displace":[{{
      - "Country": "Name of the country."
      - "Location": "The specific place within the country where the displacement occurred, and no matter the displacement is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the displacement in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "homeless": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article.
      The homelessness information can be splited into 3 parts,
      the first is the total number of homelessness caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Homeless":{{
      - "Total_Homeless": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of homelessness in the article to present the total number of homelessness,
         and if no total number of homelessness explicitly mentioned or the information is missing, assign 'NULL'."
      - "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total homelessness. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of homelessness in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Homeless_Per_Country":[{{
      - "Country": "Name of the country where the homelessness occurred, and no matter the homelessness is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in this level related to the {Event_Name}.
         Do not sum the number of homelessness in specific locations from the country to present the total number of homelessness for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of homelessness in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total homelessness in this level. The output should only include the header name."
            }}]
      the third is the specific instance of homelessness in the sub-national level caused by the {Event_Name}, make sure to capture all locations with homelessness information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Country_Homeless":[{{
      - "Country": "Name of the country."
      - "Location": "The specific place within the country where the homelessness occurred, and no matter the homelessness is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the homelessness in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "injuries": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article.
      The non-fatal injuries information can be splited into 3 parts,
      the first is the total number of non-fatal injuries caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Injury":{{
      - "Total_Injury": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of non-fatal injuries in the article to present the total number of non-fatal injuries,
         and if no total number of non-fatal injuries explicitly mentioned or the information is missing, assign 'NULL'."
      - "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total non-fatal injuries. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of non-fatal injuries in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Injury_Per_Country":[{{
      - "Country": "Name of the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in this level related to the {Event_Name}.
         Do not sum the number of non-fatal injuries in specific locations from the country to present the total number of non-fatal injuries for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of non-fatal injuries in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total non-fatal injuries in this level. The output should only include the header name."
            }}]
      the third is the specific instance of non-fatal injuries in the sub-national level caused by the {Event_Name}, make sure to capture all locations with non-fatal injuries information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Country_Injury":[{{
      - "Country": "Name of the country."
      - "Location": "The specific place within the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The number of people who got injured, hurt, wound, or hospitalized (excluding death) in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the non-fatal injuries in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "insured_damage": [
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The insured damage information can be splited into 3 parts,
            the first is the total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy,
            and organize this information in JSON format as follows:
            - "Total_Summary_Insured_Damage": {{
            - "Total_Insured_Damage": "The total amount of insured damage and make sure the information extracted for this containing the keyword "insured" or "insurance".
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of insured damage in the article to present the total number of insured damage,
               and if no total number of insured damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total insured damage. The output should only include "Info_Box" or the header name."
              }}
            the second is the total insured damage in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
             - "Insured_Damage_Per_Country":[{{
              - "Country": "Name of the country where the insured damage occured, and no matter the total insured damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Total_Insured_Damage": "The total amount of insured damage in this level related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Do not sum the insured damage in specific locations from the country to present the total insured damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion').
                 If the information is missing or if no total insured damage in this level is mentioned, assign 'NULL'."
              - "Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", and if Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total insured damage in this level. The output should only include the header name."
                  }}]
              the third is the specific instance of insured damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with insured damage information and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Country_Insured_Damage":[{{
              - "Country": "Name of the country."
              - "Location": "The specific place/places within the country where the insured damage occurred, and no matter the insured damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Insured_Damage": "The amount of insured damage in the specific location/locations related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
              - "Unit": "The currency of the insured damage, like USD, EUR. If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Inflation_Adjusted": "Indicate 'Yes' if the insured damage amount has been adjusted for inflation; otherwise "No", If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Inflation_Adjusted_Year": "The year of inflation adjustment for the insured damage, if applicable; If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the insured damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "damage": [
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the economic damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The economic damage information can be splited into 3 parts,
            the first is the total economic damage caused by the {Event_Name},
            and organize this information in JSON format as follows:
            - "Total_Summary_Economic_Damage": {{
            - "Total_Economic_Damage": "The total amount of economic damage.
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of economic damage in the article to present the total number of economic damage,
               and if no total number of economic damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total economic damage. The output should only include "Info_Box" or the header name."
              }}
            the second is the total economic damage in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
             - "Economic_Damage_Per_Country":[{{
              - "Country": "Name of the country where the economic damage occured, and no matter the total economic damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Total_Economic_Damage": "The total amount of economic damage in this level related to the {Event_Name}.
                 Do not sum the economic damage in specific locations from the country to present the total economic damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion').
                 If the information is missing or if no total economic damage in this level is mentioned, assign 'NULL'."
              - "Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", and if Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total economic damage in this level. The output should only include the header name."
                  }}]
              the third is the specific instance of economic damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with economic damage information and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Country_Economic_Damage":[{{
              - "Country": "Name of the country."
              - "Location": "The specific place/places within the country where the economic damage occurred, and no matter the economic damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Economic_Damage": "The amount of economic damage in the specific location/locations related to the {Event_Name}.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
              - "Unit": "The currency of the economic damage, like USD, EUR. If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Inflation_Adjusted": "Indicate 'Yes' if the economic damage amount has been adjusted for inflation; otherwise "No", If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Inflation_Adjusted_Year": "The year of inflation adjustment for the economic damage, if applicable; If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the economic damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "main_event_hazard": [
        """
         Based on information box {Info_Box} and header-content pair article {Whole_Text},
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
    ],
    "location_time": [
        """
        Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract time and location information associated with the {Event_Name}, along with supporting annotations from the article.
        the first is to identify the time information of the event {Event_Name}, and organize this information in JSON format as follows:
        - "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "Time_with_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the time. The output should only include "Info_Box" or the header name."
        the second is to identify all locations affected by {Event_Name} and organize this information in JSON format as follows:
        - "Location": "List all places mentioned in the text, including cities, regions, countries, and other administrative locations affected by {Event_Name}. The list should be formatted as ["location1", "location2"]."
        - "Location_with_Annotation":  "Cite "Info_Box" or the header name from the article provided where you find the information about the affected locations. The output should only include "Info_Box" or the header name."
         Only Give Json output, no extra explanation needed."""
    ],
}

# V_3 is a version based on V2, but with freezed variable names as the schema we confirmed, 20240830

V_3_1: dict = {
    "affected": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article.
      The affected people information can be splited into 3 parts,
      the first is the total number of affected people caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Affected":{{
      - "Total_Affected": "The total number of people who were affected, impacted, or influenced in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of affected people in the article to present the total number of affected people,
         and if no total number of affected people explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Affected_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total affected people. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of affected people in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Affected":[{{
      - "Administrative_Areas": "Name of the country where the affected people located, and no matter the affected people are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The total number of people who were affected, impacted, or influenced in this level related to the {Event_Name}.
         Do not sum the number of affected people in specific locations from the country to present the total number of affected people for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of affected people in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total affected people in this level. The output should only include the header name."
            }}]
      the third is the specific instance of affected people in the sub-national level caused by the {Event_Name}, make sure to capture all locations with affected people information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Affected":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the affected people located, and no matter the affected people are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The number of people who were affected, impacted, or influenced in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the affected people in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "buildings_damaged": [
        """Based on the provided article {Info_Box} {Whole_Text},
      extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting annotations from the article. The number of damaged buildings information can be splited into 3 parts,
      the first is the total number of damaged buildings caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Buildings_Damaged":{{
      - "Total_Buildings_Damaged": "The total number of damaged buildings in the {Event_Name}.
          Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
          Do not sum the number of damaged buildings in the article to present the total number of damaged buildings,
          and if no total number of damaged buildings explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Buildings_Damaged_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total number of damaged buildings. The output should only include "Info_Box" or the header name."
        }}
      the second is the total number of damaged buildings in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Buildings_Damaged":[{{
      - "Administrative_Areas": "Name of the country where the building damage occured, and no matter the building damage is in one or several countries, please order them in a list like [Country1, Country2, Country3].."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": ""The total number of damaged buildings in this level related to the {Event_Name}.
         Do not sum the number of damaged buildings in specific locations from the country to present the total number of damaged buildings for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
         If the information is missing or if no total number of damaged buildings in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total building damage in this level. The output should only include the header name."
            }}]
      the third is the specific instance of damaged buildings within each country caused by the {Event_Name}, make sure to capture all locations with damaged buildings information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Buildings_Damaged":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place/places within the country where the damaged buildings occurred, and no matter the building damage is in one or several places, order it/them in a list like ["city1";"city2";"city3"]."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": "The number of damaged buildings in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes"). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the building damage in this location. The output should only include the header name."
            }}]
      Ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "deaths": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract the number of deaths associated with the {Event_Name},
      along with supporting annotations from the article. The death information can be splited into 3 parts,
      the first is the total number of deaths caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Deaths":{{
      - "Total_Deaths": "The total number of people who died in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of death in the article to present the total number of death, and if no total number of death explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Deaths_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total death. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of deaths in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Deaths":[{{
      - "Administrative_Areas": "Name of the country where the death occurred, and no matter the deaths are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The total number of people who died in this level related to the {Event_Name}.
         Do not sum the number of death in specific locations from the country to present the total number of death for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of death in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total death in this level. The output should only include the header name."
            }}]
      the third is the specific instance of deaths in the sub-national level caused by the {Event_Name}, make sure to capture all locations with death information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Deaths":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the deaths occurred, and no matter the deaths are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The number of people who died in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the death in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "displaced": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article.
      The displacement information can be splited into 3 parts,
      the first is the total number of displacement caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Displaced":{{
      - "Total_Displaced": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of displacement in the article to present the total number of displacement,
         and if no total number of displacement explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Displaced_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total displacement. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of displacement in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Displaced":[{{
      - "Administrative_Areas": "Name of the country where the displacement occurred, and no matter the displacement is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in this level related to the {Event_Name}.
         Do not sum the number of displacement in specific locations from the country to present the total number of displacement for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of displacement in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total displacement in this level. The output should only include the header name."
            }}]
      the third is the specific instance of displacement in the sub-national level caused by the {Event_Name}, make sure to capture all locations with displacement information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Displaced":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the displacement occurred, and no matter the displacement is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the displacement in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "homeless": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article.
      The homelessness information can be splited into 3 parts,
      the first is the total number of homelessness caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Homeless":{{
      - "Total_Homeless": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of homelessness in the article to present the total number of homelessness,
         and if no total number of homelessness explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Homeless_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total homelessness. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of homelessness in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Homeless":[{{
      - "Administrative_Areas": "Name of the country where the homelessness occurred, and no matter the homelessness is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in this level related to the {Event_Name}.
         Do not sum the number of homelessness in specific locations from the country to present the total number of homelessness for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of homelessness in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total homelessness in this level. The output should only include the header name."
            }}]
      the third is the specific instance of homelessness in the sub-national level caused by the {Event_Name}, make sure to capture all locations with homelessness information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Homeless":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the homelessness occurred, and no matter the homelessness is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the homelessness in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "injuries": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article.
      The non-fatal injuries information can be splited into 3 parts,
      the first is the total number of non-fatal injuries caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Injuries":{{
      - "Total_Injuries": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of non-fatal injuries in the article to present the total number of non-fatal injuries,
         and if no total number of non-fatal injuries explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Injuries_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total non-fatal injuries. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of non-fatal injuries in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Injuries":[{{
      - "Administrative_Areas": "Name of the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in this level related to the {Event_Name}.
         Do not sum the number of non-fatal injuries in specific locations from the country to present the total number of non-fatal injuries for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of non-fatal injuries in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total non-fatal injuries in this level. The output should only include the header name."
            }}]
      the third is the specific instance of non-fatal injuries in the sub-national level caused by the {Event_Name}, make sure to capture all locations with non-fatal injuries information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Injuries":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The number of people who got injured, hurt, wound, or hospitalized (excluding death) in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the non-fatal injuries in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "insured_damage": [
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The insured damage information can be splited into 3 parts,
            the first is the total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy,
            and organize this information in JSON format as follows:
            - "Total_Summary_Insured_Damage": {{
            - "Total_Insured_Damage": "The total amount of insured damage and make sure the information extracted for this containing the keyword "insured" or "insurance".
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of insured damage in the article to present the total number of insured damage,
               and if no total number of insured damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Insured_Damage_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total insured damage. The output should only include "Info_Box" or the header name."
              }}
            the second is the total insured damage in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
             - "Instance_Per_Administrative_Areas_Insured_Damage":[{{
              - "Administrative_Areas": "Name of the country where the insured damage occured, and no matter the total insured damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The total amount of insured damage in this level related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Do not sum the insured damage in specific locations from the country to present the total insured damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion').
                 If the information is missing or if no total insured damage in this level is mentioned, assign 'NULL'."
              - "Num_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", and if Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total insured damage in this level. The output should only include the header name."
                  }}]
              the third is the specific instance of insured damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with insured damage information and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Administrative_Area_Insured_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the insured damage occurred, and no matter the insured damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The amount of insured damage in the specific location/locations related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
              - "Num_Unit": "The currency of the insured damage, like USD, EUR. If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the insured damage amount has been adjusted for inflation; otherwise "No", If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the insured damage, if applicable; If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the insured damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "damage": [
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the economic damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The economic damage information can be splited into 3 parts,
            the first is the total economic damage caused by the {Event_Name},
            and organize this information in JSON format as follows:
            - "Total_Summary_Damage": {{
            - "Total_Damage": "The total amount of economic damage.
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of economic damage in the article to present the total number of economic damage,
               and if no total number of economic damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Damage_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total economic damage. The output should only include "Info_Box" or the header name."
              }}
            the second is the total economic damage in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
             - "Instance_Per_Administrative_Areas_Damage":[{{
              - "Administrative_Areas": "Name of the country where the economic damage occured, and no matter the total economic damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The total amount of economic damage in this level related to the {Event_Name}.
                 Do not sum the economic damage in specific locations from the country to present the total economic damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion').
                 If the information is missing or if no total economic damage in this level is mentioned, assign 'NULL'."
              - "Num_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", and if Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total economic damage in this level. The output should only include the header name."
                  }}]
              the third is the specific instance of economic damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with economic damage information and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Administrative_Area_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the economic damage occurred, and no matter the economic damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The amount of economic damage in the specific location/locations related to the {Event_Name}.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
              - "Num_Unit": "The currency of the economic damage, like USD, EUR. If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the economic damage amount has been adjusted for inflation; otherwise "No", If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the economic damage, if applicable; If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the economic damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "main_event_hazard": [
        """
         Based on information box {Info_Box} and header-content pair article {Whole_Text},
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
           - "Main_Event_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the Main_Event category. The output should only include "Info_Box" or the header name."
         based on the result of the Main_Event category from the previous step and the Main_Event--Hazard table, identify the hazard information and organize this information in JSON format as follows:
           - "Hazards": "Identify the hazards of the {Event_Name}, make sure the hazards are associated with the Main_Event category from the table, and if more than one hazard is detected from the text, separate them with '|'. "
           - "Hazards_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the hazard information. The output should only include "Info_Box" or the header name."
          Only Give Json output, no extra explanation needed."""
    ],
    # in this version, we ask the model to extract all the affected locations in L1, but in the post-processing, only extract the countries in this field.
    "location_time": [
        """
        Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract time and location information associated with the {Event_Name}, along with supporting annotations from the article.
        the first is to identify the time information of the event {Event_Name}, and organize this information in JSON format as follows:
        - "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "Time_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the time. The output should only include "Info_Box" or the header name."
        the second is to identify all locations affected by {Event_Name} and organize this information in JSON format as follows:
        - "Administrative_Areas": "List all places mentioned in the text, including cities, regions, countries, and other administrative locations affected by {Event_Name}. The list should be formatted as ["location1", "location2"]."
        - "Administrative_Areas_Annotation":  "Cite "Info_Box" or the header name from the article provided where you find the information about the affected locations. The output should only include "Info_Box" or the header name."
         Only Give Json output, no extra explanation needed."""
    ],
}
V_3_2: dict = {
    "affected": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article.
      The affected people information can be splited into 3 parts,
      the first is the total number of affected people caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Affected":{{
      - "Total_Affected": "The total number of people who were affected, impacted, or influenced in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of affected people in the article to present the total number of affected people,
         and if no total number of affected people explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Affected_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total affected people. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of affected people in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Affected":[{{
      - "Administrative_Areas": "Name of the country where the affected people located, and no matter the affected people are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The total number of people who were affected, impacted, or influenced in this level related to the {Event_Name}.
         Do not sum the number of affected people in specific locations from the country to present the total number of affected people for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of affected people in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total affected people in this level. The output should only include the header name."
            }}]
      the third is the specific instance of affected people in the sub-national level caused by the {Event_Name}, make sure to capture all locations with affected people information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Affected":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the affected people located, and no matter the affected people are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The number of people who were affected, impacted, or influenced in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the affected people in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "buildings_damaged": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting annotations from the article. The number of damaged buildings information can be splited into 3 parts,
      the first is the total number of damaged buildings caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Buildings_Damaged":{{
      - "Total_Buildings_Damaged": "The total number of damaged buildings in the {Event_Name}.
          Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
          Do not sum the number of damaged buildings in the article to present the total number of damaged buildings,
          and if no total number of damaged buildings explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Buildings_Damaged_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total number of damaged buildings. The output should only include "Info_Box" or the header name."
        }}
      the second is the total number of damaged buildings in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Buildings_Damaged":[{{
      - "Administrative_Areas": "Name of the country where the building damage occured, and no matter the building damage is in one or several countries, please order them in a list like [Country1, Country2, Country3].."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": ""The total number of damaged buildings in this level related to the {Event_Name}.
         Do not sum the number of damaged buildings in specific locations from the country to present the total number of damaged buildings for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
         If the information is missing or if no total number of damaged buildings in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total building damage in this level. The output should only include the header name."
            }}]
      the third is the specific instance of damaged buildings within each country caused by the {Event_Name}, make sure to capture all locations with damaged buildings information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Buildings_Damaged":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place/places within the country where the damaged buildings occurred, and no matter the building damage is in one or several places, order it/them in a list like ["city1";"city2";"city3"]."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": "The number of damaged buildings in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes"). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the building damage in this location. The output should only include the header name."
            }}]
      Ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "deaths": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract the number of deaths associated with the {Event_Name},
      along with supporting annotations from the article. The death information can be splited into 3 parts,
      the first is the total number of deaths caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Deaths":{{
      - "Total_Deaths": "The total number of people who died in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of death in the article to present the total number of death, and if no total number of death explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Deaths_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total death. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of deaths in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Deaths":[{{
      - "Administrative_Areas": "Name of the country where the death occurred, and no matter the deaths are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The total number of people who died in this level related to the {Event_Name}.
         Do not sum the number of death in specific locations from the country to present the total number of death for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of death in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total death in this level. The output should only include the header name."
            }}]
      the third is the specific instance of deaths in the sub-national level caused by the {Event_Name}, make sure to capture all locations with death information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Deaths":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the deaths occurred, and no matter the deaths are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The number of people who died in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the death in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "displaced": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article.
      The displacement information can be splited into 3 parts,
      the first is the total number of displacement caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Displaced":{{
      - "Total_Displaced": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of displacement in the article to present the total number of displacement,
         and if no total number of displacement explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Displaced_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total displacement. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of displacement in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Displaced":[{{
      - "Administrative_Areas": "Name of the country where the displacement occurred, and no matter the displacement is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in this level related to the {Event_Name}.
         Do not sum the number of displacement in specific locations from the country to present the total number of displacement for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of displacement in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total displacement in this level. The output should only include the header name."
            }}]
      the third is the specific instance of displacement in the sub-national level caused by the {Event_Name}, make sure to capture all locations with displacement information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Displaced":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the displacement occurred, and no matter the displacement is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the displacement in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "homeless": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article.
      The homelessness information can be splited into 3 parts,
      the first is the total number of homelessness caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Homeless":{{
      - "Total_Homeless": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of homelessness in the article to present the total number of homelessness,
         and if no total number of homelessness explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Homeless_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total homelessness. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of homelessness in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Homeless":[{{
      - "Administrative_Areas": "Name of the country where the homelessness occurred, and no matter the homelessness is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in this level related to the {Event_Name}.
         Do not sum the number of homelessness in specific locations from the country to present the total number of homelessness for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of homelessness in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total homelessness in this level. The output should only include the header name."
            }}]
      the third is the specific instance of homelessness in the sub-national level caused by the {Event_Name}, make sure to capture all locations with homelessness information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Homeless":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the homelessness occurred, and no matter the homelessness is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the homelessness in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "injuries": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article.
      The non-fatal injuries information can be splited into 3 parts,
      the first is the total number of non-fatal injuries caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Injuries":{{
      - "Total_Injuries": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of non-fatal injuries in the article to present the total number of non-fatal injuries,
         and if no total number of non-fatal injuries explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Injuries_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total non-fatal injuries. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of non-fatal injuries in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Injuries":[{{
      - "Administrative_Areas": "Name of the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in this level related to the {Event_Name}.
         Do not sum the number of non-fatal injuries in specific locations from the country to present the total number of non-fatal injuries for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of non-fatal injuries in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total non-fatal injuries in this level. The output should only include the header name."
            }}]
      the third is the specific instance of non-fatal injuries in the sub-national level caused by the {Event_Name}, make sure to capture all locations with non-fatal injuries information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Injuries":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The number of people who got injured, hurt, wound, or hospitalized (excluding death) in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the non-fatal injuries in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "insured_damage": [
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The insured damage information can be splited into 3 parts,
            the first is the total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy,
            and organize this information in JSON format as follows:
            - "Total_Summary_Insured_Damage": {{
            - "Total_Insured_Damage": "The total amount of insured damage and make sure the information extracted for this containing the keyword "insured" or "insurance".
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of insured damage in the article to present the total number of insured damage,
               and if no total number of insured damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Insured_Damage_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total insured damage. The output should only include "Info_Box" or the header name."
              }}
            the second is the total insured damage in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
             - "Instance_Per_Administrative_Areas_Insured_Damage":[{{
              - "Administrative_Areas": "Name of the country where the insured damage occured, and no matter the total insured damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The total amount of insured damage in this level related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Do not sum the insured damage in specific locations from the country to present the total insured damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion').
                 If the information is missing or if no total insured damage in this level is mentioned, assign 'NULL'."
              - "Num_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", and if Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total insured damage in this level. The output should only include the header name."
                  }}]
              the third is the specific instance of insured damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with insured damage information and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Administrative_Area_Insured_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the insured damage occurred, and no matter the insured damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The amount of insured damage in the specific location/locations related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
              - "Num_Unit": "The currency of the insured damage, like USD, EUR. If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the insured damage amount has been adjusted for inflation; otherwise "No", If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the insured damage, if applicable; If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the insured damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "damage": [
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the economic damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The economic damage information can be splited into 3 parts,
            the first is the total economic damage caused by the {Event_Name},
            and organize this information in JSON format as follows:
            - "Total_Summary_Damage": {{
            - "Total_Damage": "The total amount of economic damage.
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of economic damage in the article to present the total number of economic damage,
               and if no total number of economic damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Damage_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total economic damage. The output should only include "Info_Box" or the header name."
              }}
            the second is the total economic damage in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
             - "Instance_Per_Administrative_Areas_Damage":[{{
              - "Administrative_Areas": "Name of the country where the economic damage occured, and no matter the total economic damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The total amount of economic damage in this level related to the {Event_Name}.
                 Do not sum the economic damage in specific locations from the country to present the total economic damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion').
                 If the information is missing or if no total economic damage in this level is mentioned, assign 'NULL'."
              - "Num_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", and if Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total economic damage in this level. The output should only include the header name."
                  }}]
              the third is the specific instance of economic damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with economic damage information and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Administrative_Area_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the economic damage occurred, and no matter the economic damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The amount of economic damage in the specific location/locations related to the {Event_Name}.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
              - "Num_Unit": "The currency of the economic damage, like USD, EUR. If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the economic damage amount has been adjusted for inflation; otherwise "No", If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the economic damage, if applicable; If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the economic damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "main_event_hazard": [
        """
         Based on information box {Info_Box} and header-content pair article {Whole_Text},
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
           - "Main_Event_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the Main_Event category. The output should only include "Info_Box" or the header name."
         based on the result of the Main_Event category from the previous step and the Main_Event--Hazard table, identify the hazard information and organize this information in JSON format as follows:
           - "Hazards": "Identify the hazards of the {Event_Name}, make sure the hazards are associated with the Main_Event category from the table, and if more than one hazard is detected from the text, separate them with '|'. "
           - "Hazards_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the hazard information. The output should only include "Info_Box" or the header name."
          Only Give Json output, no extra explanation needed."""
    ],
    # in this version, we ask the model to extract all the affected locations in L1, but in the post-processing, only extract the countries in this field.
    "location_time": [
        """
        Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract time and location information associated with the {Event_Name}, along with supporting annotations from the article.
        the first is to identify the time information of the event {Event_Name}, and organize this information in JSON format as follows:
        - "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "Time_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the time. The output should only include "Info_Box" or the header name."
        the second is to identify all countries affected by {Event_Name} and organize this information in JSON format as follows:
        - "Administrative_Areas": "List all countries mentioned in the text affected by {Event_Name}. The list should be formatted as ["country1", "country2"]."
        - "Administrative_Areas_Annotation":  "Cite "Info_Box" or the header name from the article provided where you find the information about the affected countries. The output should only include "Info_Box" or the header name."
         Only Give Json output, no extra explanation needed."""
    ],
}

V_3_3: dict = {
    "affected": [
        """Based on information box and header-content pair article,
      extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article.
      The affected people information can be splited into 3 parts,
      the first is the total number of affected people caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Affected":{{
      - "Total_Affected": "The total number of people who were affected, impacted, or influenced in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of affected people in the article to present the total number of affected people,
         and if no total number of affected people explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Affected_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total affected people. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of affected people in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Affected":[{{
      - "Administrative_Areas": "Name of the country where the affected people located, and no matter the affected people are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The total number of people who were affected, impacted, or influenced in this level related to the {Event_Name}.
         Do not sum the number of affected people in specific locations from the country to present the total number of affected people for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of affected people in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total affected people in this level. The output should only include the header name."
            }}]
      the third is the specific instance of affected people in the sub-national level caused by the {Event_Name}, make sure to capture all locations with affected people information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Affected":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the affected people located, and no matter the affected people are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The number of people who were affected, impacted, or influenced in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the affected people in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.  --- Info box---

--- Info box---
 {Info_Box}
--- Article---
{Whole_Text}
--- Article-- """
    ],
    "buildings_damaged": [
        """
        Based on information box and header-content pair article,
      extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting annotations from the article. The number of damaged buildings information can be splited into 3 parts,
      the first is the total number of damaged buildings caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Buildings_Damaged":{{
      - "Total_Buildings_Damaged": "The total number of damaged buildings in the {Event_Name}.
          Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
          Do not sum the number of damaged buildings in the article to present the total number of damaged buildings,
          and if no total number of damaged buildings explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Buildings_Damaged_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total number of damaged buildings. The output should only include "Info_Box" or the header name."
        }}
      the second is the total number of damaged buildings in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Buildings_Damaged":[{{
      - "Administrative_Areas": "Name of the country where the building damage occured, and no matter the building damage is in one or several countries, please order them in a list like [Country1, Country2, Country3].."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": ""The total number of damaged buildings in this level related to the {Event_Name}.
         Do not sum the number of damaged buildings in specific locations from the country to present the total number of damaged buildings for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
         If the information is missing or if no total number of damaged buildings in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total building damage in this level. The output should only include the header name."
            }}]
      the third is the specific instance of damaged buildings within each country caused by the {Event_Name}, make sure to capture all locations with damaged buildings information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Buildings_Damaged":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place/places within the country where the damaged buildings occurred, and no matter the building damage is in one or several places, order it/them in a list like ["city1";"city2";"city3"]."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": "The number of damaged buildings in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes"). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the building damage in this location. The output should only include the header name."
            }}]
      Ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.  --- Info box---

--- Info box---
 {Info_Box}
--- Article---
{Whole_Text}
--- Article-- """
    ],
    "deaths": [
        """Based on information box and header-content pair article, extract the number of deaths associated with the {Event_Name},
      along with supporting annotations from the article. The death information can be splited into 3 parts,
      the first is the total number of deaths caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Deaths":{{
      - "Total_Deaths": "The total number of people who died in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of death in the article to present the total number of death, and if no total number of death explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Deaths_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total death. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of deaths in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Deaths":[{{
      - "Administrative_Areas": "Name of the country where the death occurred, and no matter the deaths are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The total number of people who died in this level related to the {Event_Name}.
         Do not sum the number of death in specific locations from the country to present the total number of death for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of death in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total death in this level. The output should only include the header name."
            }}]
      the third is the specific instance of deaths in the sub-national level caused by the {Event_Name}, make sure to capture all locations with death information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Deaths":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the deaths occurred, and no matter the deaths are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The number of people who died in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the death in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.  --- Info box---

--- Info box---
 {Info_Box}
--- Article---
{Whole_Text}
--- Article-- """
    ],
    "displaced": [
        """Based on information box and header-content pair article,
      extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article.
      The displacement information can be splited into 3 parts,
      the first is the total number of displacement caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Displaced":{{
      - "Total_Displaced": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of displacement in the article to present the total number of displacement,
         and if no total number of displacement explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Displaced_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total displacement. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of displacement in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Displaced":[{{
      - "Administrative_Areas": "Name of the country where the displacement occurred, and no matter the displacement is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in this level related to the {Event_Name}.
         Do not sum the number of displacement in specific locations from the country to present the total number of displacement for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of displacement in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total displacement in this level. The output should only include the header name."
            }}]
      the third is the specific instance of displacement in the sub-national level caused by the {Event_Name}, make sure to capture all locations with displacement information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Displaced":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the displacement occurred, and no matter the displacement is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the displacement in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.  --- Info box---

--- Info box---
 {Info_Box}
--- Article---
{Whole_Text}
--- Article-- """
    ],
    "homeless": [
        """Based on information box and header-content pair article,
      extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article.
      The homelessness information can be splited into 3 parts,
      the first is the total number of homelessness caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Homeless":{{
      - "Total_Homeless": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of homelessness in the article to present the total number of homelessness,
         and if no total number of homelessness explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Homeless_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total homelessness. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of homelessness in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Homeless":[{{
      - "Administrative_Areas": "Name of the country where the homelessness occurred, and no matter the homelessness is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in this level related to the {Event_Name}.
         Do not sum the number of homelessness in specific locations from the country to present the total number of homelessness for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of homelessness in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total homelessness in this level. The output should only include the header name."
            }}]
      the third is the specific instance of homelessness in the sub-national level caused by the {Event_Name}, make sure to capture all locations with homelessness information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Homeless":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the homelessness occurred, and no matter the homelessness is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the homelessness in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.  --- Info box---

--- Info box---
 {Info_Box}
--- Article---
{Whole_Text}
--- Article-- """
    ],
    "injuries": [
        """Based on information box and header-content pair article,
      extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article.
      The non-fatal injuries information can be splited into 3 parts,
      the first is the total number of non-fatal injuries caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Injuries":{{
      - "Total_Injuries": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of non-fatal injuries in the article to present the total number of non-fatal injuries,
         and if no total number of non-fatal injuries explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Injuries_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total non-fatal injuries. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of non-fatal injuries in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Injuries":[{{
      - "Administrative_Areas": "Name of the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in this level related to the {Event_Name}.
         Do not sum the number of non-fatal injuries in specific locations from the country to present the total number of non-fatal injuries for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of non-fatal injuries in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total non-fatal injuries in this level. The output should only include the header name."
            }}]
      the third is the specific instance of non-fatal injuries in the sub-national level caused by the {Event_Name}, make sure to capture all locations with non-fatal injuries information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Injuries":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The number of people who got injured, hurt, wound, or hospitalized (excluding death) in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the non-fatal injuries in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.  --- Info box---

--- Info box---
 {Info_Box}
--- Article---
{Whole_Text}
--- Article-- """
    ],
    "insured_damage": [
        """
            Based on information box and header-content pair article,
            extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The insured damage information can be splited into 3 parts,
            the first is the total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy,
            and organize this information in JSON format as follows:
            - "Total_Summary_Insured_Damage": {{
            - "Total_Insured_Damage": "The total amount of insured damage and make sure the information extracted for this containing the keyword "insured" or "insurance".
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of insured damage in the article to present the total number of insured damage,
               and if no total number of insured damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Insured_Damage_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total insured damage. The output should only include "Info_Box" or the header name."
              }}
            the second is the total insured damage in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
             - "Instance_Per_Administrative_Areas_Insured_Damage":[{{
              - "Administrative_Areas": "Name of the country where the insured damage occured, and no matter the total insured damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The total amount of insured damage in this level related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Do not sum the insured damage in specific locations from the country to present the total insured damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion').
                 If the information is missing or if no total insured damage in this level is mentioned, assign 'NULL'."
              - "Num_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", and if Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total insured damage in this level. The output should only include the header name."
                  }}]
              the third is the specific instance of insured damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with insured damage information and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Administrative_Area_Insured_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the insured damage occurred, and no matter the insured damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The amount of insured damage in the specific location/locations related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
              - "Num_Unit": "The currency of the insured damage, like USD, EUR. If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the insured damage amount has been adjusted for inflation; otherwise "No", If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the insured damage, if applicable; If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the insured damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.  --- Info box---

--- Info box---
 {Info_Box}
--- Article---
{Whole_Text}
--- Article-- """
    ],
    "damage": [
        """
            Based on information box and header-content pair article,
            extract the economic damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The economic damage information can be splited into 3 parts,
            the first is the total economic damage caused by the {Event_Name},
            and organize this information in JSON format as follows:
            - "Total_Summary_Damage": {{
            - "Total_Damage": "The total amount of economic damage.
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of economic damage in the article to present the total number of economic damage,
               and if no total number of economic damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Damage_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total economic damage. The output should only include "Info_Box" or the header name."
              }}
            the second is the total economic damage in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
             - "Instance_Per_Administrative_Areas_Damage":[{{
              - "Administrative_Areas": "Name of the country where the economic damage occured, and no matter the total economic damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The total amount of economic damage in this level related to the {Event_Name}.
                 Do not sum the economic damage in specific locations from the country to present the total economic damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion').
                 If the information is missing or if no total economic damage in this level is mentioned, assign 'NULL'."
              - "Num_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", and if Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total economic damage in this level. The output should only include the header name."
                  }}]
              the third is the specific instance of economic damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with economic damage information and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Administrative_Area_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the economic damage occurred, and no matter the economic damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The amount of economic damage in the specific location/locations related to the {Event_Name}.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
              - "Num_Unit": "The currency of the economic damage, like USD, EUR. If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the economic damage amount has been adjusted for inflation; otherwise "No", If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the economic damage, if applicable; If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the economic damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.  --- Info box---

--- Info box---
 {Info_Box}
--- Article---
{Whole_Text}
--- Article-- """
    ],
    "main_event_hazard": [
        """
         Based on information box and header-content pair article,
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
           - "Main_Event_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the Main_Event category. The output should only include "Info_Box" or the header name."
         based on the result of the Main_Event category from the previous step and the Main_Event--Hazard table, identify the hazard information and organize this information in JSON format as follows:
           - "Hazards": "Identify the hazards of the {Event_Name}, make sure the hazards are associated with the Main_Event category from the table, and if more than one hazard is detected from the text, separate them with '|'. "
           - "Hazards_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the hazard information. The output should only include "Info_Box" or the header name."
          Only Give Json output, no extra explanation needed.  --- Info box---

--- Info box---
 {Info_Box}
--- Article---
{Whole_Text}
--- Article--"""
    ],
    # in this version, we ask the model to extract all the affected locations in L1, but in the post-processing, only extract the countries in this field.
    "location_time": [
        """
        Based on information box and header-content pair article, extract time and location information associated with the {Event_Name}, along with supporting annotations from the article.
        the first is to identify the time information of the event {Event_Name}, and organize this information in JSON format as follows:
        - "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "Time_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the time. The output should only include "Info_Box" or the header name."
        the second is to identify all countries affected by {Event_Name} and organize this information in JSON format as follows:
        - "Administrative_Areas": "List all countries mentioned in the text affected by {Event_Name}. The list should be formatted as ["country1", "country2"]."
        - "Administrative_Areas_Annotation":  "Cite "Info_Box" or the header name from the article provided where you find the information about the affected countries. The output should only include "Info_Box" or the header name."
         Only Give Json output, no extra explanation needed.  --- Info box---

--- Info box---
 {Info_Box}
--- Article---
{Whole_Text}
--- Article--"""
    ],
}


V_3_Country: dict = {
    # in this version, we ask the model to extract all the affected countries in L1.
    "location_time": [
        """
        Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract affected countries information associated with the {Event_Name}, along with supporting annotations from the article.
          the task is to identify all countries affected by {Event_Name} and organize this information in JSON format as follows:
        - "Administrative_Areas": "List all countries mentioned in the text affected by {Event_Name}. The list should be formatted as ["Country1", "Country2"]."
        - "Administrative_Areas_Annotation":  "Cite "Info_Box" or the header name from the article provided where you find the information about the affected countries. The output should only include "Info_Box" or the header name."
         Only Give Json output, no extra explanation needed."""
    ],
}
# V_4 is the one with two prompts for each impact category
V_4_impact: dict = {
    "affected": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article.
      The affected people information can be splited into 2 parts,
      the first is the total number of affected people caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Affected":{{
      - "Total_Affected": "The total number of people who were affected, impacted, or influenced in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of affected people in the article to present the total number of affected people,
         and if no total number of affected people explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Affected_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total affected people. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of affected people in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Affected":[{{
      - "Administrative_Areas": "Name of the country where the affected people located, and no matter the affected people are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The total number of people who were affected, impacted, or influenced in this level related to the {Event_Name}.
         Do not sum the number of affected people in specific locations from the country to present the total number of affected people for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of affected people in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total affected people in this level. The output should only include the header name."
            }}]
         Ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article.
      The information is the specific instance of affected people in the sub-national level caused by the {Event_Name},
        make sure to capture all locations with affected people information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Affected":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the affected people located, and no matter the affected people are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The number of people who were affected, impacted, or influenced in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the affected people in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "buildings_damaged": [
        """Based on the provided article {Info_Box} {Whole_Text},
      extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting annotations from the article. The number of damaged buildings information can be splited into 2 parts,
      the first is the total number of damaged buildings caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Buildings_Damaged":{{
      - "Total_Buildings_Damaged": "The total number of damaged buildings in the {Event_Name}.
          Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
          Do not sum the number of damaged buildings in the article to present the total number of damaged buildings,
          and if no total number of damaged buildings explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Buildings_Damaged_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total number of damaged buildings. The output should only include "Info_Box" or the header name."
        }}
      the second is the total number of damaged buildings in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Buildings_Damaged":[{{
      - "Administrative_Areas": "Name of the country where the building damage occured, and no matter the building damage is in one or several countries, please order them in a list like [Country1, Country2, Country3].."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": ""The total number of damaged buildings in this level related to the {Event_Name}.
         Do not sum the number of damaged buildings in specific locations from the country to present the total number of damaged buildings for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
         If the information is missing or if no total number of damaged buildings in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total building damage in this level. The output should only include the header name."
            }}]
         Ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
        """ Based on the provided article {Info_Box} {Whole_Text},
      extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting annotations from the article. The information is the specific instance of damaged buildings within each country caused by the {Event_Name}, make sure to capture all locations with damaged buildings information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Buildings_Damaged":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place/places within the country where the damaged buildings occurred, and no matter the building damage is in one or several places, order it/them in a list like ["city1";"city2";"city3"]."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": "The number of damaged buildings in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes"). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the building damage in this location. The output should only include the header name."
            }}]
      Ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "deaths": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract the number of deaths associated with the {Event_Name},
      along with supporting annotations from the article. The death information can be splited into 2 parts ,
      the first is the total number of deaths caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Deaths":{{
      - "Total_Deaths": "The total number of people who died in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of death in the article to present the total number of death, and if no total number of death explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Deaths_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total death. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of deaths in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Deaths":[{{
      - "Administrative_Areas": "Name of the country where the death occurred, and no matter the deaths are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The total number of people who died in this level related to the {Event_Name}.
         Do not sum the number of death in specific locations from the country to present the total number of death for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of death in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total death in this level. The output should only include the header name."
            }}]
         Ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract the number of deaths associated with the {Event_Name},
      along with supporting annotations from the article. The information is the specific instance of deaths in the sub-national level caused by the {Event_Name}, make sure to capture all locations with death information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Deaths":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the deaths occurred, and no matter the deaths are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The number of people who died in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the death in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "displaced": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article.
      The displacement information can be splited into 2 parts ,
      the first is the total number of displacement caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Displaced":{{
      - "Total_Displaced": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of displacement in the article to present the total number of displacement,
         and if no total number of displacement explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Displaced_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total displacement. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of displacement in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Displaced":[{{
      - "Administrative_Areas": "Name of the country where the displacement occurred, and no matter the displacement is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in this level related to the {Event_Name}.
         Do not sum the number of displacement in specific locations from the country to present the total number of displacement for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of displacement in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total displacement in this level. The output should only include the header name."
            }}]
         Ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article. The information is the specific instance of displacement in the sub-national level caused by the {Event_Name}, make sure to capture all locations with displacement information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Displaced":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the displacement occurred, and no matter the displacement is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the displacement in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "homeless": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article.
      The homelessness information can be splited into 2 parts ,
      the first is the total number of homelessness caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Homeless":{{
      - "Total_Homeless": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of homelessness in the article to present the total number of homelessness,
         and if no total number of homelessness explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Homeless_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total homelessness. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of homelessness in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Homeless":[{{
      - "Administrative_Areas": "Name of the country where the homelessness occurred, and no matter the homelessness is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in this level related to the {Event_Name}.
         Do not sum the number of homelessness in specific locations from the country to present the total number of homelessness for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of homelessness in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total homelessness in this level. The output should only include the header name."
            }}]
         Ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article. The information is the specific instance of homelessness in the sub-national level caused by the {Event_Name}, make sure to capture all locations with homelessness information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Homeless":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the homelessness occurred, and no matter the homelessness is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the homelessness in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "injuries": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article.
      The non-fatal injuries information can be splited into 2 parts ,
      the first is the total number of non-fatal injuries caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Injuries":{{
      - "Total_Injuries": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of non-fatal injuries in the article to present the total number of non-fatal injuries,
         and if no total number of non-fatal injuries explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Injuries_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total non-fatal injuries. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of non-fatal injuries in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Injuries":[{{
      - "Administrative_Areas": "Name of the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in this level related to the {Event_Name}.
         Do not sum the number of non-fatal injuries in specific locations from the country to present the total number of non-fatal injuries for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of non-fatal injuries in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total non-fatal injuries in this level. The output should only include the header name."}}]
         Ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article. The information is the specific instance of non-fatal injuries in the sub-national level caused by the {Event_Name}, make sure to capture all locations with non-fatal injuries information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Injuries":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The number of people who got injured, hurt, wound, or hospitalized (excluding death) in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the non-fatal injuries in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "insured_damage": [
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The insured damage information can be splited into 2 parts ,
            the first is the total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy,
            and organize this information in JSON format as follows:
            - "Total_Summary_Insured_Damage": {{
            - "Total_Insured_Damage": "The total amount of insured damage and make sure the information extracted for this containing the keyword "insured" or "insurance".
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of insured damage in the article to present the total number of insured damage,
               and if no total number of insured damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Insured_Damage_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total insured damage. The output should only include "Info_Box" or the header name."
              }}
            the second is the total insured damage in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
             - "Instance_Per_Administrative_Areas_Insured_Damage":[{{
              - "Administrative_Areas": "Name of the country where the insured damage occured, and no matter the total insured damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The total amount of insured damage in this level related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Do not sum the insured damage in specific locations from the country to present the total insured damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion').
                 If the information is missing or if no total insured damage in this level is mentioned, assign 'NULL'."
              - "Num_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", and if Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total insured damage in this level. The output should only include the header name."
                  }}]
                   Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
                extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article. The information is the specific instance of insured damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with insured damage information, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy, and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Administrative_Area_Insured_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the insured damage occurred, and no matter the insured damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The amount of insured damage in the specific location/locations related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
              - "Num_Unit": "The currency of the insured damage, like USD, EUR. If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the insured damage amount has been adjusted for inflation; otherwise "No", If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the insured damage, if applicable; If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the insured damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "damage": [
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the economic damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The economic damage information can be splited into 2 parts ,
            the first is the total economic damage caused by the {Event_Name},
            and organize this information in JSON format as follows:
            - "Total_Summary_Damage": {{
            - "Total_Damage": "The total amount of economic damage.
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of economic damage in the article to present the total number of economic damage,
               and if no total number of economic damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Damage_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total economic damage. The output should only include "Info_Box" or the header name."
              }}
            the second is the total economic damage in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
             - "Instance_Per_Administrative_Areas_Damage":[{{
              - "Administrative_Areas": "Name of the country where the economic damage occured, and no matter the total economic damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The total amount of economic damage in this level related to the {Event_Name}.
                 Do not sum the economic damage in specific locations from the country to present the total economic damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion').
                 If the information is missing or if no total economic damage in this level is mentioned, assign 'NULL'."
              - "Num_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", and if Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total economic damage in this level. The output should only include the header name."
                  }}]
               Ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the economic damage information associated with the {Event_Name}, along with supporting annotations from the article. The information is the specific instance of economic damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with economic damage information and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Administrative_Area_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the economic damage occurred, and no matter the economic damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The amount of economic damage in the specific location/locations related to the {Event_Name}.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
              - "Num_Unit": "The currency of the economic damage, like USD, EUR. If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the economic damage amount has been adjusted for inflation; otherwise "No", If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the economic damage, if applicable; If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the economic damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
}


# V_5 is the one with three prompts for each impact category, can only feed the L1 and L2, because L3 is feeded in the V_4, but make things easy, just feed all of them, and for testing
V_5: dict = {
    "affected": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article.
      The information is the total number of affected people caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Affected":{{
      - "Total_Affected": "The total number of people who were affected, impacted, or influenced in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of affected people in the article to present the total number of affected people,
         and if no total number of affected people explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Affected_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total affected people. The output should only include "Info_Box" or the header name."
      }}
      Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article.
      The information is the total number of affected people in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Affected":[{{
      - "Administrative_Areas": "Name of the country where the affected people located, and no matter the affected people are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The total number of people who were affected, impacted, or influenced in this level related to the {Event_Name}.
         Do not sum the number of affected people in specific locations from the country to present the total number of affected people for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of affected people in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total affected people in this level. The output should only include the header name."
            }}]
         Ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article.
      The information is the specific instance of affected people in the sub-national level caused by the {Event_Name},
        make sure to capture all locations with affected people information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Affected":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the affected people located, and no matter the affected people are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The number of people who were affected, impacted, or influenced in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the affected people in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "buildings_damaged": [
        """Based on the provided article {Info_Box} {Whole_Text},
      extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting annotations from the article. The number of damaged buildings information can be splited into 2 parts,
      The information is the total number of damaged buildings caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Buildings_Damaged":{{
      - "Total_Buildings_Damaged": "The total number of damaged buildings in the {Event_Name}.
          Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
          Do not sum the number of damaged buildings in the article to present the total number of damaged buildings,
          and if no total number of damaged buildings explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Buildings_Damaged_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total number of damaged buildings. The output should only include "Info_Box" or the header name."
        }} Only Give Json output, no extra explanation needed.""",
        """Based on the provided article {Info_Box} {Whole_Text},
      extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting annotations from the article.The information is the total number of damaged buildings in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Buildings_Damaged":[{{
      - "Administrative_Areas": "Name of the country where the building damage occured, and no matter the building damage is in one or several countries, please order them in a list like [Country1, Country2, Country3].."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": ""The total number of damaged buildings in this level related to the {Event_Name}.
         Do not sum the number of damaged buildings in specific locations from the country to present the total number of damaged buildings for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
         If the information is missing or if no total number of damaged buildings in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total building damage in this level. The output should only include the header name."
            }}]
         Ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
        """ Based on the provided article {Info_Box} {Whole_Text},
      extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting annotations from the article. The information is the specific instance of damaged buildings within each country caused by the {Event_Name}, make sure to capture all locations with damaged buildings information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Buildings_Damaged":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place/places within the country where the damaged buildings occurred, and no matter the building damage is in one or several places, order it/them in a list like ["city1";"city2";"city3"]."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": "The number of damaged buildings in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes"). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the building damage in this location. The output should only include the header name."
            }}]
      Ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "deaths": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract the number of deaths associated with the {Event_Name},
      along with supporting annotations from
      The information is the total number of deaths caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Deaths":{{
      - "Total_Deaths": "The total number of people who died in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of death in the article to present the total number of death, and if no total number of death explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Deaths_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total death. The output should only include "Info_Box" or the header name."
      }} Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract the number of deaths associated with the {Event_Name},
      along with supporting annotations from the article. The information is the total number of deaths in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Deaths":[{{
      - "Administrative_Areas": "Name of the country where the death occurred, and no matter the deaths are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The total number of people who died in this level related to the {Event_Name}.
         Do not sum the number of death in specific locations from the country to present the total number of death for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of death in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total death in this level. The output should only include the header name."
            }}]
         Ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract the number of deaths associated with the {Event_Name},
      along with supporting annotations from the article. The information is the specific instance of deaths in the sub-national level caused by the {Event_Name}, make sure to capture all locations with death information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Deaths":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the deaths occurred, and no matter the deaths are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The number of people who died in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the death in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "displaced": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article.

      The information is the total number of displacement caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Displaced":{{
      - "Total_Displaced": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of displacement in the article to present the total number of displacement,
         and if no total number of displacement explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Displaced_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total displacement. The output should only include "Info_Box" or the header name."
      }}Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article. The information is the total number of displacement in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Displaced":[{{
      - "Administrative_Areas": "Name of the country where the displacement occurred, and no matter the displacement is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in this level related to the {Event_Name}.
         Do not sum the number of displacement in specific locations from the country to present the total number of displacement for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of displacement in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total displacement in this level. The output should only include the header name."
            }}]
         Ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article. The information is the specific instance of displacement in the sub-national level caused by the {Event_Name}, make sure to capture all locations with displacement information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Displaced":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the displacement occurred, and no matter the displacement is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the displacement in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "homeless": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article.

      The information is the total number of homelessness caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Homeless":{{
      - "Total_Homeless": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of homelessness in the article to present the total number of homelessness,
         and if no total number of homelessness explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Homeless_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total homelessness. The output should only include "Info_Box" or the header name."
      }}Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article.The information is the total number of homelessness in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Homeless":[{{
      - "Administrative_Areas": "Name of the country where the homelessness occurred, and no matter the homelessness is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in this level related to the {Event_Name}.
         Do not sum the number of homelessness in specific locations from the country to present the total number of homelessness for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of homelessness in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total homelessness in this level. The output should only include the header name."
            }}]
         Ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article. The information is the specific instance of homelessness in the sub-national level caused by the {Event_Name}, make sure to capture all locations with homelessness information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Homeless":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the homelessness occurred, and no matter the homelessness is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the homelessness in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "injuries": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article.

      The information is the total number of non-fatal injuries caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Injuries":{{
      - "Total_Injuries": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of non-fatal injuries in the article to present the total number of non-fatal injuries,
         and if no total number of non-fatal injuries explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Injuries_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total non-fatal injuries. The output should only include "Info_Box" or the header name."
      }}Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article. The information is the total number of non-fatal injuries in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Injuries":[{{
      - "Administrative_Areas": "Name of the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in this level related to the {Event_Name}.
         Do not sum the number of non-fatal injuries in specific locations from the country to present the total number of non-fatal injuries for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         If the information is missing or if no total number of non-fatal injuries in this level is mentioned, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total non-fatal injuries in this level. The output should only include the header name."}}]
         Ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article. The information is the specific instance of non-fatal injuries in the sub-national level caused by the {Event_Name}, make sure to capture all locations with non-fatal injuries information and organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Injuries":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The number of people who got injured, hurt, wound, or hospitalized (excluding death) in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). If the information is missing, assign 'NULL'."
      - "Annotation": "Cite the header name from the article provided where you find the information about the non-fatal injuries in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "insured_damage": [
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article.

            The information is the total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy,
            and organize this information in JSON format as follows:
            - "Total_Summary_Insured_Damage": {{
            - "Total_Insured_Damage": "The total amount of insured damage and make sure the information extracted for this containing the keyword "insured" or "insurance".
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of insured damage in the article to present the total number of insured damage,
               and if no total number of insured damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Insured_Damage_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total insured damage. The output should only include "Info_Box" or the header name."
              }} Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The information is the total insured damage in the country level caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy,
            and organize this information in JSON format as follows:
             - "Instance_Per_Administrative_Areas_Insured_Damage":[{{
              - "Administrative_Areas": "Name of the country where the insured damage occured, and no matter the total insured damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The total amount of insured damage in this level related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Do not sum the insured damage in specific locations from the country to present the total insured damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion').
                 If the information is missing or if no total insured damage in this level is mentioned, assign 'NULL'."
              - "Num_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", and if Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total insured damage in this level. The output should only include the header name."
                  }}]
                   Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
                extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article. The information is the specific instance of insured damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with insured damage information, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy, and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Administrative_Area_Insured_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the insured damage occurred, and no matter the insured damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The amount of insured damage in the specific location/locations related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
              - "Num_Unit": "The currency of the insured damage, like USD, EUR. If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the insured damage amount has been adjusted for inflation; otherwise "No", If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the insured damage, if applicable; If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the insured damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
    "damage": [
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the economic damage information associated with the {Event_Name}, along with supporting annotations from the article.

            The information is the total economic damage caused by the {Event_Name},
            and organize this information in JSON format as follows:
            - "Total_Summary_Damage": {{
            - "Total_Damage": "The total amount of economic damage.
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of economic damage in the article to present the total number of economic damage,
               and if no total number of economic damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Damage_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total economic damage. The output should only include "Info_Box" or the header name."
              }} Only Give Json output, no extra explanation needed.""",
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the economic damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The information is the total economic damage in the country level caused by the {Event_Name}, and organize this information in JSON format as follows:
             - "Instance_Per_Administrative_Areas_Damage":[{{
              - "Administrative_Areas": "Name of the country where the economic damage occured, and no matter the total economic damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The total amount of economic damage in this level related to the {Event_Name}.
                 Do not sum the economic damage in specific locations from the country to present the total economic damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion').
                 If the information is missing or if no total economic damage in this level is mentioned, assign 'NULL'."
              - "Num_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", and if Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total economic damage in this level. The output should only include the header name."
                  }}]
               Ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed.""",
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the economic damage information associated with the {Event_Name}, along with supporting annotations from the article. The information is the specific instance of economic damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with economic damage information and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Administrative_Area_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the economic damage occurred, and no matter the economic damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The amount of economic damage in the specific location/locations related to the {Event_Name}.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion'). If the information is missing, assign 'NULL'."
              - "Num_Unit": "The currency of the economic damage, like USD, EUR. If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the economic damage amount has been adjusted for inflation; otherwise "No", If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the economic damage, if applicable; If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the economic damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """,
    ],
}


V_6: dict = {
    "affected": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of affected people associated with the {Event_Name}, along with supporting annotations from the article.
      The affected people information can be splited into 3 parts,
      the first is the total number of affected people caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Affected":{{
      - "Total_Affected": "The total number of people who were affected, impacted, or influenced in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of affected people in the article to present the total number of affected people,
         and if no total number of affected people explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Affected_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total affected people. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of affected people in the country level caused by the {Event_Name}, in this part, "NULL" is forbidden for the items "Administrative_Areas" and "Num". These fields require real, existing information, and cannot be left empty or undefined.
      Please organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Affected":[{{
      - "Administrative_Areas": "Name of the country where the affected people located, and no matter the affected people are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the people were affected, if mentioned, otherwise, NULL."
      - "End_Date":"The end date when the people were affected, if mentioned, otherwise, NULL."
      - "Num": "The total number of people who were affected, impacted, or influenced in this level related to the {Event_Name}.
         Do not sum the number of affected people in specific locations from the country to present the total number of affected people for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
      - "Annotation": "Cite the header name from the article provided where you find the information about the total affected people in this level. The output should only include the header name."
            }}]
      the third is the specific instance of affected people in the sub-national level caused by the {Event_Name}, make sure to capture all locations with affected people information, in this part, "NULL" is forbidden for the items "Administrative_Area", "Locations", and "Num". These fields require real, existing information, and cannot be left empty or undefined.
      Please organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Affected":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the affected people located, and no matter the affected people are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the people were affected, if mentioned, otherwise, NULL."
      - "End_Date":"The end date when the people were affected, if mentioned, otherwise, NULL."
      - "Num": "The number of people who were affected, impacted, or influenced in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name from the article provided where you find the information about the affected people in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "buildings_damaged": [
        """Based on the provided article {Info_Box} {Whole_Text},
      extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting annotations from the article. The number of damaged buildings information can be splited into 3 parts,
      the first is the total number of damaged buildings caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Buildings_Damaged":{{
      - "Total_Buildings_Damaged": "The total number of damaged buildings in the {Event_Name}.
          Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
          Do not sum the number of damaged buildings in the article to present the total number of damaged buildings,
          and if no total number of damaged buildings explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Buildings_Damaged_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total number of damaged buildings. The output should only include "Info_Box" or the header name."
        }}
      the second is the total number of damaged buildings in the country level caused by the {Event_Name}, in this part, "NULL" is forbidden for the items "Administrative_Areas" and "Num". These fields require real, existing information, and cannot be left empty or undefined. Please organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Buildings_Damaged":[{{
      - "Administrative_Areas": "Name of the country where the building damage occured, and no matter the building damage is in one or several countries, please order them in a list like [Country1, Country2, Country3].."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned, otherwise, NULL."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned, otherwise, NULL."
      - "Num": ""The total number of damaged buildings in this level related to the {Event_Name}.
         Do not sum the number of damaged buildings in specific locations from the country to present the total number of damaged buildings for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes")."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total building damage in this level. The output should only include the header name."
            }}]
      the third is the specific instance of damaged buildings within each country caused by the {Event_Name}, make sure to capture all locations with damaged buildings information, in this part, "NULL" is forbidden for the items "Administrative_Area", "Locations", and "Num". These fields require real, existing information, and cannot be left empty or undefined. Please organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Buildings_Damaged":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place/places within the country where the damaged buildings occurred, and no matter the building damage is in one or several places, order it/them in a list like ["city1";"city2";"city3"]."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned, otherwise, NULL."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned, otherwise, NULL."
      - "Num": "The number of damaged buildings in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes")."
      - "Annotation": "Cite the header name from the article provided where you find the information about the building damage in this location. The output should only include the header name."
            }}]
      Ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "deaths": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract the number of deaths associated with the {Event_Name},
      along with supporting annotations from the article. The death information can be splited into 3 parts,
      the first is the total number of deaths caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Deaths":{{
      - "Total_Deaths": "The total number of people who died in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of death in the article to present the total number of death, and if no total number of death explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Deaths_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total death. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of deaths in the country level caused by the {Event_Name}, in this part, "NULL" is forbidden for the items "Administrative_Areas" and "Num". These fields require real, existing information, and cannot be left empty or undefined. Please organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Deaths":[{{
      - "Administrative_Areas": "Name of the country where the death occurred, and no matter the deaths are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned, otherwise, NULL."
      - "End_Date":"The end date when the deaths occurred, if mentioned, otherwise, NULL."
      - "Num": "The total number of people who died in this level related to the {Event_Name}.
         Do not sum the number of death in specific locations from the country to present the total number of death for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total death in this level. The output should only include the header name."
            }}]
      the third is the specific instance of deaths in the sub-national level caused by the {Event_Name}, make sure to capture all locations with death information, in this part, "NULL" is forbidden for the items "Administrative_Area", "Locations", and "Num". These fields require real, existing information, and cannot be left empty or undefined. Please organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Deaths":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the deaths occurred, and no matter the deaths are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the deaths occurred, if mentioned, otherwise, NULL."
      - "End_Date":"The end date when the deaths occurred, if mentioned, otherwise, NULL."
      - "Num": "The number of people who died in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name from the article provided where you find the information about the death in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "displaced": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of displacement associated with the {Event_Name}, along with supporting annotations from the article.
      The displacement information can be splited into 3 parts,
      the first is the total number of displacement caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Displaced":{{
      - "Total_Displaced": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of displacement in the article to present the total number of displacement,
         and if no total number of displacement explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Displaced_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total displacement. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of displacement in the country level caused by the {Event_Name}, in this part, "NULL" is forbidden for the items "Administrative_Areas" and "Num". These fields require real, existing information, and cannot be left empty or undefined. Please organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Displaced":[{{
      - "Administrative_Areas": "Name of the country where the displacement occurred, and no matter the displacement is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned, otherwise, NULL."
      - "End_Date":"The end date when the displacement occurred, if mentioned, otherwise, NULL."
      - "Num": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in this level related to the {Event_Name}.
         Do not sum the number of displacement in specific locations from the country to present the total number of displacement for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total displacement in this level. The output should only include the header name."
            }}]
      the third is the specific instance of displacement in the sub-national level caused by the {Event_Name}, make sure to capture all locations with displacement information, in this part, "NULL" is forbidden for the items "Administrative_Area", "Locations", and "Num". These fields require real, existing information, and cannot be left empty or undefined. Please organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Displaced":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the displacement occurred, and no matter the displacement is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the displacement occurred, if mentioned, otherwise, NULL."
      - "End_Date":"The end date when the displacement occurred, if mentioned, otherwise, NULL."
      - "Num": "The number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name from the article provided where you find the information about the displacement in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "homeless": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of homelessness associated with the {Event_Name}, along with supporting annotations from the article.
      The homelessness information can be splited into 3 parts,
      the first is the total number of homelessness caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Homeless":{{
      - "Total_Homeless": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of homelessness in the article to present the total number of homelessness,
         and if no total number of homelessness explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Homeless_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total homelessness. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of homelessness in the country level caused by the {Event_Name}, in this part, "NULL" is forbidden for the items "Administrative_Areas" and "Num". These fields require real, existing information, and cannot be left empty or undefined. Please organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Homeless":[{{
      - "Administrative_Areas": "Name of the country where the homelessness occurred, and no matter the homelessness is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned, otherwise, NULL."
      - "End_Date":"The end date when the homelessness occurred, if mentioned, otherwise, NULL."
      - "Num": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in this level related to the {Event_Name}.
         Do not sum the number of homelessness in specific locations from the country to present the total number of homelessness for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total homelessness in this level. The output should only include the header name."
            }}]
      the third is the specific instance of homelessness in the sub-national level caused by the {Event_Name}, make sure to capture all locations with homelessness information, in this part, "NULL" is forbidden for the items "Administrative_Area", "Locations", and "Num". These fields require real, existing information, and cannot be left empty or undefined. Please organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Homeless":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the homelessness occurred, and no matter the homelessness is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned, otherwise, NULL."
      - "End_Date":"The end date when the homelessness occurred, if mentioned, otherwise, NULL."
      - "Num": "The number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name from the article provided where you find the information about the homelessness in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "injuries": [
        """Based on information box {Info_Box} and header-content pair article {Whole_Text},
      extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting annotations from the article.
      The non-fatal injuries information can be splited into 3 parts,
      the first is the total number of non-fatal injuries caused by the {Event_Name}, and organize this information in JSON format as follows:
      - "Total_Summary_Injuries":{{
      - "Total_Injuries": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of non-fatal injuries in the article to present the total number of non-fatal injuries,
         and if no total number of non-fatal injuries explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Injuries_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total non-fatal injuries. The output should only include "Info_Box" or the header name."
      }}
      the second is the total number of non-fatal injuries in the country level caused by the {Event_Name}, in this part, "NULL" is forbidden for the items "Administrative_Areas" and "Num". These fields require real, existing information, and cannot be left empty or undefined. Please organize this information in JSON format as follows:
      - "Instance_Per_Administrative_Areas_Injuries":[{{
      - "Administrative_Areas": "Name of the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several countries, please order them in a list like [Country1, Country2, Country3]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned, otherwise, NULL."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned, otherwise, NULL."
      - "Num": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in this level related to the {Event_Name}.
         Do not sum the number of non-fatal injuries in specific locations from the country to present the total number of non-fatal injuries for this level information.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name from the article provided where you find the information about the total non-fatal injuries in this level. The output should only include the header name."
            }}]
      the third is the specific instance of non-fatal injuries in the sub-national level caused by the {Event_Name}, make sure to capture all locations with non-fatal injuries information, in this part, "NULL" is forbidden for the items "Administrative_Area", "Locations", and "Num". These fields require real, existing information, and cannot be left empty or undefined. Please organize this information in JSON format as follows:
      - "Specific_Instance_Per_Administrative_Area_Injuries":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]."
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned, otherwise, NULL."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned, otherwise, NULL."
      - "Num": "The number of people who got injured, hurt, wound, or hospitalized (excluding death) in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name from the article provided where you find the information about the non-fatal injuries in this location. The output should only include the header name."
       }}]
      Ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "insured_damage": [
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the insured damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The insured damage information can be splited into 3 parts,
            the first is the total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy,
            and organize this information in JSON format as follows:
            - "Total_Summary_Insured_Damage": {{
            - "Total_Insured_Damage": "The total amount of insured damage and make sure the information extracted for this containing the keyword "insured" or "insurance".
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of insured damage in the article to present the total number of insured damage,
               and if no total number of insured damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Insured_Damage_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total insured damage. The output should only include "Info_Box" or the header name."
              }}
            the second is the total insured damage in the country level caused by the {Event_Name}, in this part, "NULL" is forbidden for the items "Administrative_Areas" and "Num". These fields require real, existing information, and cannot be left empty or undefined. Please organize this information in JSON format as follows:
             - "Instance_Per_Administrative_Areas_Insured_Damage":[{{
              - "Administrative_Areas": "Name of the country where the insured damage occured, and no matter the total insured damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned, otherwise, NULL."
              - "End_Date":"The end date when the insured damage occurred, if mentioned, otherwise, NULL."
              - "Num": "The total amount of insured damage in this level related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Do not sum the insured damage in specific locations from the country to present the total insured damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion')."
              - "Num_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", and if Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total insured damage in this level. The output should only include the header name."
                  }}]
              the third is the specific instance of insured damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with insured damage information, in this part, "NULL" is forbidden for the items "Administrative_Area", "Locations", "Num", and "Num_Unit". These fields require real, existing information, and cannot be left empty or undefined. and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Administrative_Area_Insured_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the insured damage occurred, and no matter the insured damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the insured damage occurred, if mentioned, otherwise, NULL."
              - "End_Date":"The end date when the insured damage occurred, if mentioned, otherwise, NULL."
              - "Num": "The amount of insured damage in the specific location/locations related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion')."
              - "Num_Unit": "The currency of the insured damage, like USD, EUR. If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the insured damage amount has been adjusted for inflation; otherwise "No", If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the insured damage, if applicable; If Insured_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the insured damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "damage": [
        """
            Based on information box {Info_Box} and header-content pair article {Whole_Text},
            extract the economic damage information associated with the {Event_Name}, along with supporting annotations from the article.
            The economic damage information can be splited into 3 parts,
            the first is the total economic damage caused by the {Event_Name},
            and organize this information in JSON format as follows:
            - "Total_Summary_Damage": {{
            - "Total_Damage": "The total amount of economic damage.
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of economic damage in the article to present the total number of economic damage,
               and if no total number of economic damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Damage_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total economic damage. The output should only include "Info_Box" or the header name."
              }}
            the second is the total economic damage in the country level caused by the {Event_Name}, in this part, "NULL" is forbidden for the items "Administrative_Areas" and "Num". These fields require real, existing information, and cannot be left empty or undefined. Please organize this information in JSON format as follows:
             - "Instance_Per_Administrative_Areas_Damage":[{{
              - "Administrative_Areas": "Name of the country where the economic damage occured, and no matter the total economic damage is in one or several countries, please order them in a list like [Country1, Country2, Country3]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned, otherwise, NULL."
              - "End_Date":"The end date when the economic damage occurred, if mentioned, otherwise, NULL."
              - "Num": "The total amount of economic damage in this level related to the {Event_Name}.
                 Do not sum the economic damage in specific locations from the country to present the total economic damage for this level information.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion')."
              - "Num_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", and if Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the total economic damage in this level. The output should only include the header name."
                  }}]
              the third is the specific instance of economic damage in the sub-national level caused by the {Event_Name}, make sure to capture all locations with economic damage information, in this part, "NULL" is forbidden for the items "Administrative_Area", "Locations", "Num" and "Num_Unit". These fields require real, existing information, and cannot be left empty or undefined. and organize this information in JSON format as follows:
              - "Specific_Instance_Per_Administrative_Area_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the economic damage occurred, and no matter the economic damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned, otherwise, NULL."
              - "End_Date":"The end date when the economic damage occurred, if mentioned, otherwise, NULL."
              - "Num": "The amount of economic damage in the specific location/locations related to the {Event_Name}.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion')."
              - "Num_Unit": "The currency of the economic damage, like USD, EUR. If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the economic damage amount has been adjusted for inflation; otherwise "No", If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the economic damage, if applicable; If Economic_Damage is missing from the previous step, assign 'NULL'."
              - "Annotation": "Cite the header name from the article provided where you find the information about the economic damage in this location. The output should only include the header name."

                 }}]
            Ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. """
    ],
    "main_event_hazard": [
        """
         Based on information box {Info_Box} and header-content pair article {Whole_Text},
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
           - "Main_Event_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the Main_Event category. The output should only include "Info_Box" or the header name."
         based on the result of the Main_Event category from the previous step and the Main_Event--Hazard table, identify the hazard information and organize this information in JSON format as follows:
           - "Hazards": "Identify the hazards of the {Event_Name}, make sure the hazards are associated with the Main_Event category from the table, and if more than one hazard is detected from the text, separate them with '|'. "
           - "Hazards_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the hazard information. The output should only include "Info_Box" or the header name."
          Only Give Json output, no extra explanation needed."""
    ],
    # in this version, we ask the model to extract all the affected locations in L1, but in the post-processing, only extract the countries in this field.
    "location_time": [
        """
        Based on information box {Info_Box} and header-content pair article {Whole_Text}, extract time and location information associated with the {Event_Name}, along with supporting annotations from the article.
        the first is to identify the time information of the event {Event_Name}, and organize this information in JSON format as follows:
        - "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "Time_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the time. The output should only include "Info_Box" or the header name."
        the second is to identify all countries affected by {Event_Name} and organize this information in JSON format as follows:
        - "Administrative_Areas": "List all countries mentioned in the text affected by {Event_Name}. The list should be formatted as ["Country1", "Country2"]."
        - "Administrative_Areas_Annotation":  "Cite "Info_Box" or the header name from the article provided where you find the information about the affected countries. The output should only include "Info_Box" or the header name."
         Only Give Json output, no extra explanation needed."""
    ],
}



#for wikimpacts v2, we use structured output and batch api with o3 mini model 



# the schema for multi event prompting, include all output in one schema 
def generate_MultiEvent() -> dict: 
   return {
    "type": "json_schema",
   

    "json_schema": {
       "name": "MultiEvent_response",
      "strict": True,
       "schema": {
        "type": "object",
        "properties": {
           
            "Start_Date": {"type": "string"},
            "End_Date": {"type": "string"},
            "Time_Annotation": {"type": "string"},
            "Administrative_Areas": {
                "type": "array",
                "items": {"type": "string"}
            },
            "Administrative_Areas_Annotation": {"type": "string"},
            "Main_Event": {"type": "string"},
            "Main_Event_Annotation": {"type": "string"},
            "Hazards": {"type": "string"},
            "Hazards_Annotation": {"type": "string"},
             "Total_Summary_Affected": {
                            "type": "object",
                            "properties": {
                                f"Total_Affected": {"type": "string"},
                                f"Total_Affected_Annotation": {"type": "string"}
                                },
                            "required": [f"Total_Affected", f"Total_Affected_Annotation"],
                            "additionalProperties": False 
                    },
               "Specific_Instance_Per_Administrative_Area_Affected": {
                        "type": "array",
                        "items": { 
                            "type": "object",
                            "properties": {
                                "Administrative_Area": {"type": "string"},
                                "Locations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Start_Date": {"type": "string"},
                                "End_Date": {"type": "string"},
                                "Num": {"type": "string"},
                                "Annotation": {"type": "string"}
                            },
                            "required": [
                                "Start_Date", "End_Date", "Administrative_Area",
                                "Annotation", "Locations", "Num"
                            ],
                            "additionalProperties": False
                        },
                  
                  "Total_Summary_Buildings_Damaged": {
                            "type": "object",
                            "properties": {
                                f"Total_Buildings_Damaged": {"type": "string"},
                                f"Total_Buildings_Damaged_Annotation": {"type": "string"}
                                },
                            "required": [f"Total_Buildings_Damaged", f"Total_Buildings_Damaged_Annotation"],
                            "additionalProperties": False 
                    },
               "Specific_Instance_Per_Administrative_Area_Buildings_Damaged": {
                        "type": "array",
                        "items": { 
                            "type": "object",
                            "properties": {
                                "Administrative_Area": {"type": "string"},
                                "Locations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Start_Date": {"type": "string"},
                                "End_Date": {"type": "string"},
                                "Num": {"type": "string"},
                                "Annotation": {"type": "string"}
                            },
                            "required": [
                                "Start_Date", "End_Date", "Administrative_Area",
                                "Annotation", "Locations", "Num"
                            ],
                            "additionalProperties": False
                        },
                  
                  "Total_Summary_Deaths": {
                            "type": "object",
                            "properties": {
                                f"Total_Deaths": {"type": "string"},
                                f"Total_Deaths_Annotation": {"type": "string"}
                                },
                            "required": [f"Total_Deaths", f"Total_Deaths_Annotation"],
                            "additionalProperties": False 
                    },
               "Specific_Instance_Per_Administrative_Area_Deaths": {
                        "type": "array",
                        "items": { 
                            "type": "object",
                            "properties": {
                                "Administrative_Area": {"type": "string"},
                                "Locations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Start_Date": {"type": "string"},
                                "End_Date": {"type": "string"},
                                "Num": {"type": "string"},
                                "Annotation": {"type": "string"}
                            },
                            "required": [
                                "Start_Date", "End_Date", "Administrative_Area",
                                "Annotation", "Locations", "Num"
                            ],
                            "additionalProperties": False
                        },
                  
                  "Total_Summary_Displaced": {
                            "type": "object",
                            "properties": {
                                f"Total_Displaced": {"type": "string"},
                                f"Total_Displaced_Annotation": {"type": "string"}
                                },
                            "required": [f"Total_Displaced", f"Total_Displaced_Annotation"],
                            "additionalProperties": False 
                    },
               "Specific_Instance_Per_Administrative_Area_Displaced": {
                        "type": "array",
                        "items": { 
                            "type": "object",
                            "properties": {
                                "Administrative_Area": {"type": "string"},
                                "Locations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Start_Date": {"type": "string"},
                                "End_Date": {"type": "string"},
                                "Num": {"type": "string"},
                                "Annotation": {"type": "string"}
                            },
                            "required": [
                                "Start_Date", "End_Date", "Administrative_Area",
                                "Annotation", "Locations", "Num"
                            ],
                            "additionalProperties": False
                        },
                  
                  "Total_Summary_Homeless": {
                            "type": "object",
                            "properties": {
                                f"Total_Homeless": {"type": "string"},
                                f"Total_Homeless_Annotation": {"type": "string"}
                                },
                            "required": [f"Total_Homeless", f"Total_Homeless_Annotation"],
                            "additionalProperties": False 
                    },
               "Specific_Instance_Per_Administrative_Area_Homeless": {
                        "type": "array",
                        "items": { 
                            "type": "object",
                            "properties": {
                                "Administrative_Area": {"type": "string"},
                                "Locations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Start_Date": {"type": "string"},
                                "End_Date": {"type": "string"},
                                "Num": {"type": "string"},
                                "Annotation": {"type": "string"}
                            },
                            "required": [
                                "Start_Date", "End_Date", "Administrative_Area",
                                "Annotation", "Locations", "Num"
                            ],
                            "additionalProperties": False
                        },
                  
                  "Total_Summary_Injuries": {
                            "type": "object",
                            "properties": {
                                f"Total_Injuries": {"type": "string"},
                                f"Total_Injuries_Annotation": {"type": "string"}
                                },
                            "required": [f"Total_Injuries", f"Total_Injuries_Annotation"],
                            "additionalProperties": False 
                    },
               "Specific_Instance_Per_Administrative_Area_Injuries": {
                        "type": "array",
                        "items": { 
                            "type": "object",
                            "properties": {
                                "Administrative_Area": {"type": "string"},
                                "Locations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Start_Date": {"type": "string"},
                                "End_Date": {"type": "string"},
                                "Num": {"type": "string"},
                                "Annotation": {"type": "string"}
                            },
                            "required": [
                                "Start_Date", "End_Date", "Administrative_Area",
                                "Annotation", "Locations", "Num"
                            ],
                            "additionalProperties": False
                        },
                  
                "Total_Summary_Insured_Damage": {
                      
                      
                            "type": "object",
                            "properties": {
                                "Total_Insured_Damage": {"type": "string"},
                                "Total_Insured_Damage_Annotation": {"type": "string"},
                                "Total_Insured_Damage_Unit": {"type": "string"},
                                "Total_Insured_Damage_Inflation_Adjusted": {"type": "string"},
                                "Total_Insured_Damage_Inflation_Adjusted_Year": {"type": "string"}}
                            ,
                            "required": [
                                "Total_Insured_Damage", f"Total_Insured_Damage_Annotation", 
                                "Total_Insured_Damage_Unit", f"Total_Insured_Damage_Inflation_Adjusted",
                                "Total_Insured_Damage_Inflation_Adjusted_Year"
                            ],
                            "additionalProperties": False
                        
                    }, 

                    "Specific_Instance_Per_Administrative_Area_Insured_Damage": {
                        "type": "array",
                        "items": { 
                            "type": "object",
                            "properties": {
                                "Administrative_Area": {"type": "string"},
                                "Locations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Start_Date": {"type": "string"},
                                "End_Date": {"type": "string"},
                                "Num": {"type": "string"},
                                "Num_Unit": {"type": "string"},
                                "Num_Inflation_Adjusted": {"type": "string"},
                                "Num_Inflation_Adjusted_Year": {"type": "string"},
                                "Annotation": {"type": "string"}
                            },
                            "required": [
                                "Start_Date", "End_Date", "Administrative_Area", "Annotation",
                                "Locations", "Num", "Num_Unit", 
                                "Num_Inflation_Adjusted", "Num_Inflation_Adjusted_Year"
                            ],
                            "additionalProperties": False
                        }
                    },

                     "Total_Summary_Damage": {
                      
                      
                            "type": "object",
                            "properties": {
                                "Total_Damage": {"type": "string"},
                                "Total_Damage_Annotation": {"type": "string"},
                                "Total_Damage_Unit": {"type": "string"},
                                "Total_Damage_Inflation_Adjusted": {"type": "string"},
                                "Total_Damage_Inflation_Adjusted_Year": {"type": "string"}}
                            ,
                            "required": [
                                f"Total_Damage", f"Total_Damage_Annotation", 
                                f"Total_Damage_Unit", f"Total_Damage_Inflation_Adjusted",
                                f"Total_Damage_Inflation_Adjusted_Year"
                            ],
                            "additionalProperties": False
                        
                    }, 

                    "Specific_Instance_Per_Administrative_Area_Damage": {
                        "type": "array",
                        "items": { 
                            "type": "object",
                            "properties": {
                                "Administrative_Area": {"type": "string"},
                                "Locations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Start_Date": {"type": "string"},
                                "End_Date": {"type": "string"},
                                "Num": {"type": "string"},
                                "Num_Unit": {"type": "string"},
                                "Num_Inflation_Adjusted": {"type": "string"},
                                "Num_Inflation_Adjusted_Year": {"type": "string"},
                                "Annotation": {"type": "string"}
                            },
                            "required": [
                                "Start_Date", "End_Date", "Administrative_Area", "Annotation",
                                "Locations", "Num", "Num_Unit", 
                                "Num_Inflation_Adjusted", "Num_Inflation_Adjusted_Year"
                            ],
                            "additionalProperties": False
                        }
                    }
      
                } "additionalProperties": False,
        "required": ["Start_Date", "End_Date", "Administrative_Areas" ,"Time_Annotation","Administrative_Areas_Annotation",
        "Main_Event", "Main_Event_Annotation", "Hazards" ,"Hazards_Annotation", "Total_Summary_Damage","Total_Summary_Buildings_Damaged",
        "Total_Summary_Affected", "Total_Summary_Deaths","Total_Summary_Displaced","Total_Summary_Homeless","Total_Summary_Injuries", "Total_Summary_Insured_Damage" ,
        "Specific_Instance_Per_Administrative_Area_Damage","Specific_Instance_Per_Administrative_Area_Damage","Specific_Instance_Per_Administrative_Area_Damage",
        "Specific_Instance_Per_Administrative_Area_Damage","Specific_Instance_Per_Administrative_Area_Damage","Specific_Instance_Per_Administrative_Area_Damage",
        "Specific_Instance_Per_Administrative_Area_Damage","Specific_Instance_Per_Administrative_Area_Damage"]}
    }
   
}



# the schema for single event prompting, for different categories 
def generate_TotalLocationEvent() -> dict:
   return {
    "type": "json_schema",
   

    "json_schema": {
       "name": "Location_time_response",
      "strict": True,
       "schema": {
        "type": "object",
        "properties": {
           
            "Start_Date": {"type": "string"},
            "End_Date": {"type": "string"},
            "Time_Annotation": {"type": "string"},
            "Administrative_Areas": {
                "type": "array",
                "items": {"type": "string"}
            },
            "Administrative_Areas_Annotation": {"type": "string"}
        },
         "additionalProperties": False,
        "required": ["Start_Date", "End_Date", "Administrative_Areas" ,"Time_Annotation","Administrative_Areas_Annotation"]}
    }
   
}
def generate_TotalMainEvent() -> dict:
   return {
    "type": "json_schema",
 
    "json_schema": { 
         "name": "Event_Hazards__response",
      "strict": True,
      "schema": {
        "type": "object",
        "properties": {
           
            "Main_Event": {"type": "string"},
            "Main_Event_Annotation": {"type": "string"},
            "Hazards": {"type": "string"},
         
            "Hazards_Annotation": {"type": "string"}
        },
         "additionalProperties": False,
        "required": ["Main_Event", "Main_Event_Annotation", "Hazards" ,"Hazards_Annotation"]
    }}
}
def generate_total_direct_schema(impact: str) -> dict:
    
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "Direct_impact_response",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {   
                    f"Total_Summary_{impact}": {
                       
                       
                            "type": "object",
                            "properties": {
                                f"Total_{impact}": {"type": "string"},
                                f"Total_{impact}_Annotation": {"type": "string"}
                                },
                            "required": [f"Total_{impact}", f"Total_{impact}_Annotation"],
                            "additionalProperties": False
                        
                    },
                    f"Specific_Instance_Per_Administrative_Area_{impact}": {
                        "type": "array",
                        "items": { 
                            "type": "object",
                            "properties": {
                                "Administrative_Area": {"type": "string"},
                                "Locations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Start_Date": {"type": "string"},
                                "End_Date": {"type": "string"},
                                "Num": {"type": "string"},
                                "Annotation": {"type": "string"}
                            },
                            "required": [
                                "Start_Date", "End_Date", "Administrative_Area",
                                "Annotation", "Locations", "Num"
                            ],
                            "additionalProperties": False
                        }
                    }
                },
                "required": [
                    f"Total_Summary_{impact}", 
                    f"Specific_Instance_Per_Administrative_Area_{impact}"
                ],
                "additionalProperties": False
            }
        }
    }

def generate_total_monetary_schema(impact: str) -> dict:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "Monetary_impact_response",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": { 
                    f"Total_Summary_{impact}": {
                      
                      
                            "type": "object",
                            "properties": {
                                f"Total_{impact}": {"type": "string"},
                                f"Total_{impact}_Annotation": {"type": "string"},
                                f"Total_{impact}_Unit": {"type": "string"},
                                f"Total_{impact}_Inflation_Adjusted": {"type": "string"},
                                f"Total_{impact}_Inflation_Adjusted_Year": {"type": "string"}}
                            ,
                            "required": [
                                f"Total_{impact}", f"Total_{impact}_Annotation", 
                                f"Total_{impact}_Unit", f"Total_{impact}_Inflation_Adjusted",
                                f"Total_{impact}_Inflation_Adjusted_Year"
                            ],
                            "additionalProperties": False
                        
                    }, 

                    f"Specific_Instance_Per_Administrative_Area_{impact}": {
                        "type": "array",
                        "items": { 
                            "type": "object",
                            "properties": {
                                "Administrative_Area": {"type": "string"},
                                "Locations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Start_Date": {"type": "string"},
                                "End_Date": {"type": "string"},
                                "Num": {"type": "string"},
                                "Num_Unit": {"type": "string"},
                                "Num_Inflation_Adjusted": {"type": "string"},
                                "Num_Inflation_Adjusted_Year": {"type": "string"},
                                "Annotation": {"type": "string"}
                            },
                            "required": [
                                "Start_Date", "End_Date", "Administrative_Area", "Annotation",
                                "Locations", "Num", "Num_Unit", 
                                "Num_Inflation_Adjusted", "Num_Inflation_Adjusted_Year"
                            ],
                            "additionalProperties": False
                        }
                    }
                },
                "required": [
                    f"Specific_Instance_Per_Administrative_Area_{impact}", 
                    f"Total_Summary_{impact}"
                ],
                "additionalProperties": False
            }
        }
    }


def generate_LocationEvent() -> dict:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "Location_response",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "Location_Chains": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                },
                "additionalProperties": False,
                "required": ["Location_Chains"]
            }
        }
    }



Post_location =f"""Using the provided country {Administrative_Area} and a list of locations {Locations}, 
trace the administrative hierarchy for each location back to one level below the country. 
For each location, construct an array that represents the hierarchy. """

# the prompt to check if the item in the list or the section, or the tables are about climate extreme events, if yes, continue the rest prompts

def check_Event() -> dict:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "Checking_event_response",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "Checking_response": {"type": "string"},
                    "Reason":{"type": "string"}
                        
                    },
                },
                "additionalProperties": False,
                "required": ["Checking_response"]
            }
        }
checking_event=    f"""Using the provided content {content}, 
determine if it describes information related to a climate event. Respond with "Yes" or "No", 
followed by the reason for your judgment."""
# for single event: 
V_7: dict = {
    "affected": [
        """Based on the information box and header-content article given,
      extract the number of affected people associated with the {Event_Name}, along with supporting source sections from the article.
      The affected people information can be splited into 2 parts,
      the first is the total number of affected people caused by the {Event_Name}, 
      - "Total_Affected": "The total number of people who were affected, impacted, or influenced in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of affected people in the article to present the total number of affected people,
         and if no total number of affected people explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Affected_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total affected people. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
    
      the second is the specific instance of affected people caused by the {Event_Name}, do not aggregate the information on affected people from different locations; instead, retain the data exactly as presented in the original text, make sure to capture all locations with affected people information,
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the affected people located, and no matter the affected people are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'. "
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The number of people who were affected, impacted, or influenced in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name and the setences from the article provided where you find the information about the affected people,time, and locations if available."
   
      Take your time to read the whole text provided by the user, ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. 
      """
  
    
    ],

    "buildings_damaged": [
        """Based on information box and header-content pair article given,
      extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting source sections from the article. The number of damaged buildings information can be splited into 2 parts,
      the first is the total number of damaged buildings caused by the {Event_Name}, and organize this information in JSON format as follows:

      - "Total_Buildings_Damaged": "The total number of damaged buildings in the {Event_Name}.
          Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
          Do not sum the number of damaged buildings in the article to present the total number of damaged buildings,
          and if no total number of damaged buildings explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Buildings_Damaged_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total number of damaged buildings. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
   
      the second is the specific instance of damaged buildings caused by the {Event_Name}, do not aggregate the information on damaged buildings from different locations; instead, retain the data exactly as presented in the original text, make sure to capture all locations with damaged buildings information and organize this information in JSON format as follows:

      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place/places within the country where the damaged buildings occurred, and no matter the building damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": "The number of damaged buildings in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes"). "
      - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the building damages, time and location if available. "
      
       Take your time to read the whole text provided by the user, ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes.  
      """
    ],

    "deaths": [
        """Based on information box and header-content pair article given, extract the number of deaths associated with the {Event_Name},
      along with supporting source sections from the article. The death information can be splited into 2 parts,
      the first is the total number of deaths caused by the {Event_Name}, 
      - "Total_Deaths": "The total number of people who died in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of death in the article to present the total number of death, and if no total number of death explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Deaths_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total death. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
      the second is the specific instance of deaths caused by the {Event_Name}, do not aggregate the information on deaths from different locations; instead, retain the data exactly as presented in the original text, make sure to capture all locations with death information,
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the deaths occurred, and no matter the deaths are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The number of people who died in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). "
      - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the deaths, time and locations if available."
       }}]
       Take your time to read the whole text provided by the user, ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. 
"""
    ],
    "displaced": [
        """Based on information box and header-content pair article given,
      extract the number of displacement associated with the {Event_Name}, along with supporting source sections from the article.
      The displacement information can be splited into 2 parts,
      the first is the total number of displacement caused by the {Event_Name}, 
      - "Total_Displaced": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of displacement in the article to present the total number of displacement,
         and if no total number of displacement explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Displaced_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total displacement. Besides, if the information is not from the Info_Box, cite the setences where you find the information."

      the second is the specific instance of displacement caused by the {Event_Name}, do not aggregate the information on displacement from different locations; instead, retain the data exactly as presented in the original text, make sure to capture all locations with displacement information:
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the displacement occurred, and no matter the displacement is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL"
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the displacement, time and locations. "
       Take your time to read the whole text provided by the user, ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes.  """
    ],

    "homeless": [
        """Based on information box and header-content pair article given,
      extract the number of homelessness associated with the {Event_Name}, along with supporting source sections from the article.
      The homelessness information can be splited into 2 parts,
      the first is the total number of homelessness caused by the {Event_Name}, 
      - "Total_Homeless": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of homelessness in the article to present the total number of homelessness,
         and if no total number of homelessness explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Homeless_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total homelessness.  Besides, if the information is not from the Info_Box, cite the setences where you find the information."
      the second is the specific instance of homelessness caused by the {Event_Name}, do not aggregate the information on homelessness from different locations; instead, retain the data exactly as presented in the original text, make sure to capture all locations with homelessness information:
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the homelessness occurred, and no matter the homelessness is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). "
      - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the homelessness, time and location if available."
       Take your time to read the whole text provided by the user, ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes.  """
    ],
    "injuries": [
        """Based on information box and header-content pair article given,
      extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting source sections from the article.
      The non-fatal injuries information can be splited into 2 parts,
      the first is the total number of non-fatal injuries caused by the {Event_Name}, 
      - "Total_Injuries": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of non-fatal injuries in the article to present the total number of non-fatal injuries,
         and if no total number of non-fatal injuries explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Injuries_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total non-fatal injuries. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
      the second is the specific instance of non-fatal injuries caused by the {Event_Name}, do not aggregate the information on injuries from different locations; instead, retain the data exactly as presented in the original text, make sure to capture all locations with non-fatal injuries information:
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'. "
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The number of people who got injured, hurt, wound, or hospitalized (excluding death) in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). "
      - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the non-fatal injuries, time and locations if available. "
       Take your time to read the whole text provided by the user, ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes.  """
    ],
    "insured_damage": [
        """
           Based on information box and header-content pair article given,
            extract the insured damage information associated with the {Event_Name}, along with supporting source sections from the article.
            The insured damage information can be splited into 2 parts,
            the first is the total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy,
            - "Total_Insured_Damage": "The total amount of insured damage and make sure the information extracted for this containing the keyword "insured" or "insurance".
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of insured damage in the article to present the total number of insured damage,
               and if no total number of insured damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Insured_Damage_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total insured damage. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
              the second is the specific instance of insured damage caused by the {Event_Name}, do not aggregate the information on insured damage from different locations; instead, retain the data exactly as presented in the original text, make sure to capture all locations with insured damage information:
              - "Specific_Instance_Per_Administrative_Area_Insured_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the insured damage occurred, and no matter the insured damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'. "
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The amount of insured damage in the specific location/locations related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion')."
              - "Num_Unit": "The currency of the insured damage, like USD, EUR. "
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the insured damage amount has been adjusted for inflation; otherwise "No"."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the insured damage, if applicable."
              - "Annotation": "Cite the header name and sentences from the article provided where you find the information about the insured damage, time and locations if available. "
             Take your time to read the whole text provided by the user, ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. """
    ],
    "damage": [
        """
            Based on information box and header-content pair article given,
            extract the economic damage information associated with the {Event_Name}, along with supporting source sections from the article.
            The economic damage information can be splited into 2 parts,
            the first is the total economic damage caused by the {Event_Name},
            - "Total_Damage": "The total amount of economic damage.
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of economic damage in the article to present the total number of economic damage,
               and if no total number of economic damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Damage_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total economic damage. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
              the second is the specific instance of economic damage in the sub-national level caused by the {Event_Name}, do not aggregate the information on economic damage from different locations; instead, retain the data exactly as presented in the original text, make sure to capture all locations with economic damage information:
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the economic damage occurred, and no matter the economic damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The amount of economic damage in the specific location/locations related to the {Event_Name}.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion')."
              - "Num_Unit": "The currency of the economic damage, like USD, EUR. "
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the economic damage amount has been adjusted for inflation; otherwise "No"."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the economic damage, if applicable."
              - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the economic damage, time and locations if available."

                 }}]
             Take your time to read the whole text provided by the user, ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. """
    ],


    "main_event_hazard": [
        """
         Based on information box and header-content pair article,
         extract main_event category and hazard information associated with the {Event_Name}, along with supporting source sections from the article.
         Below is the Main_Event--Hazard association table,
         Main Event: Flood; Hazard: Flood
         Main Event: Extratropical Storm/Cyclone; Hazards: Wind; Flood; Blizzard; Hail
         Main Event: Tropical Storm/Cyclone; Hazards: Wind; Flood; Lightning
         Main Event: Extreme Temperature; Hazards: Heatwave; Cold Spell
         Main Event: Drought; Hazard: Drought
         Main Event: Wildfire; Hazard: Wildfire
         Main Event: Tornado; Hazard: Wind
         first identify the Main_Event category information from the text, 
           - "Main_Event": "identify the event category of the {Event_Name} referring the Main_Event--Hazard table, and only one Main_Event category should be assigned."
           - "Main_Event_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the Main_Event category. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
         based on the result of the Main_Event category from the previous step and the Main_Event--Hazard table, identify the hazard information and organize this information in JSON format as follows:
           - "Hazards": "Identify the hazards of the {Event_Name}, make sure the hazards are associated with the Main_Event category from the table, and if more than one hazard is detected from the text, separate them with '|'. "
           - "Hazards_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the hazard information. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
        
        Take your time to read the whole text provided by the user, and answer the questions."""
    ],
    # in this version, we ask the model to extract all the affected locations in L1, but in the post-processing, only extract the countries in this field.
    "location_time": [
        """
        Based on information box and header-content pair article, extract time and location information associated with the {Event_Name}, along with supporting source sections from the article.
        the first is to identify the time information of the event {Event_Name}:
        - "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "Time_Annotation": "Cite "Info_Box" or the header name or the sentences from the article provided where you find the information about the time."
        the second is to identify all countries affected by {Event_Name}:
        - "Administrative_Areas": "List all countries mentioned in the text affected by {Event_Name}. The list should be formatted as ["country1", "country2"]."
        - "Administrative_Areas_Annotation":  "Cite "Info_Box" or the header name or the sentences from the article provided where you find the information about the affected countries."
         Take your time to read the whole text provided by the user, and answer the questions."""
    ],
}

# v7_1 is the version that based on V7, but require the model give one confirmed massage for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise) and same time. 
# after evaluation, we will choose this version to continue , below is for single event
V_7_1: dict = {
    "Affected": [
        """Based on the information box and header-content article given,
      extract the number of affected people associated with the {Event_Name}, along with supporting source sections from the article.
      The affected people information can be splited into 2 parts,
      the first is the total number of affected people caused by the {Event_Name}, 
      - "Total_Affected": "The total number of people who were affected, impacted, or influenced in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of affected people in the article to present the total number of affected people,
         and if no total number of affected people explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Affected_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total affected people. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
    
      the second is the specific instance of affected people caused by the {Event_Name}, 
      do not aggregate the information on affected people from different locations; instead, 
      retain the data exactly as presented in the original text, 
      make sure to capture all locations with affected people information, 
      if multiple sentences mention the affected people information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
      retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the affected people located, and no matter the affected people are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'. "
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The number of people who were affected, impacted, or influenced in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name and the setences from the article provided where you find the information about the affected people,time, and locations if available."
   
      Take your time to read the whole text provided by the user, ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. 
      """
  
    
    ],

    "Buildings_Damaged": [
        """Based on information box and header-content pair article given,
      extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting source sections from the article. The number of damaged buildings information can be splited into 2 parts,
      the first is the total number of damaged buildings caused by the {Event_Name}, and organize this information in JSON format as follows:

      - "Total_Buildings_Damaged": "The total number of damaged buildings in the {Event_Name}.
          Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
          Do not sum the number of damaged buildings in the article to present the total number of damaged buildings,
          and if no total number of damaged buildings explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Buildings_Damaged_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total number of damaged buildings. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
   
      the second is the specific instance of damaged buildings caused by the {Event_Name}, 
      do not aggregate the information on damaged buildings from different locations; 
      instead, retain the data exactly as presented in the original text, 
      make sure to capture all locations with damaged buildings information,  
      if multiple sentences mention the buildings damaged information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
      retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place/places within the country where the damaged buildings occurred, and no matter the building damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": "The number of damaged buildings in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes"). "
      - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the building damages, time and location if available. "
      
       Take your time to read the whole text provided by the user, ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes.  
      """
    ],

    "Deaths": [
        """Based on information box and header-content pair article given, extract the number of deaths associated with the {Event_Name},
      along with supporting source sections from the article. The death information can be splited into 2 parts,
      the first is the total number of deaths caused by the {Event_Name}, 
      - "Total_Deaths": "The total number of people who died in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of death in the article to present the total number of death, and if no total number of death explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Deaths_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total death. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
      the second is the specific instance of deaths caused by the {Event_Name}, 
      do not aggregate the information on deaths from different locations; 
      instead, retain the data exactly as presented in the original text,
       make sure to capture all locations with death information,
       if multiple sentences mention the deaths information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
      retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the deaths occurred, and no matter the deaths are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The number of people who died in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). "
      - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the deaths, time and locations if available."
       }}]
       Take your time to read the whole text provided by the user, ensure to capture all instances of death mentioned in the article, including direct and indirect causes. Only Give Json output, no extra explanation needed. 
"""
    ],
    "Displaced": [
        """Based on information box and header-content pair article given,
      extract the number of displacement associated with the {Event_Name}, along with supporting source sections from the article.
      The displacement information can be splited into 2 parts,
      the first is the total number of displacement caused by the {Event_Name}, 
      - "Total_Displaced": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of displacement in the article to present the total number of displacement,
         and if no total number of displacement explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Displaced_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total displacement. Besides, if the information is not from the Info_Box, cite the setences where you find the information."

      the second is the specific instance of displacement caused by the {Event_Name},
       do not aggregate the information on displacement from different locations; 
       instead, retain the data exactly as presented in the original text, 
       make sure to capture all locations with displacement information,
       if multiple sentences mention the displaced people information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
      retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the displacement occurred, and no matter the displacement is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL"
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the displacement, time and locations. "
       Take your time to read the whole text provided by the user, ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes.  """
    ],

    "Homeless": [
        """Based on information box and header-content pair article given,
      extract the number of homelessness associated with the {Event_Name}, along with supporting source sections from the article.
      The homelessness information can be splited into 2 parts,
      the first is the total number of homelessness caused by the {Event_Name}, 
      - "Total_Homeless": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of homelessness in the article to present the total number of homelessness,
         and if no total number of homelessness explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Homeless_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total homelessness.  Besides, if the information is not from the Info_Box, cite the setences where you find the information."
      the second is the specific instance of homelessness caused by the {Event_Name}, 
      do not aggregate the information on homelessness from different locations;
       instead, retain the data exactly as presented in the original text, 
       make sure to capture all locations with homelessness information,
       if multiple sentences mention the homeless people information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
      retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the homelessness occurred, and no matter the homelessness is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). "
      - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the homelessness, time and location if available."
       Take your time to read the whole text provided by the user, ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes.  """
    ],

    "Injuries": [
        """Based on information box and header-content pair article given,
      extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting source sections from the article.
      The non-fatal injuries information can be splited into 2 parts,
      the first is the total number of non-fatal injuries caused by the {Event_Name}, 
      - "Total_Injuries": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of non-fatal injuries in the article to present the total number of non-fatal injuries,
         and if no total number of non-fatal injuries explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Injuries_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total non-fatal injuries. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
      the second is the specific instance of non-fatal injuries caused by the {Event_Name}, 
      do not aggregate the information on injuries from different locations; 
      instead, retain the data exactly as presented in the original text, 
      make sure to capture all locations with non-fatal injuries information,
      if multiple sentences mention the non-fatal injuries information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
      retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'. "
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The number of people who got injured, hurt, wound, or hospitalized (excluding death) in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). "
      - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the non-fatal injuries, time and locations if available. "
       Take your time to read the whole text provided by the user, ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes.  """
    ],
    "Insured_Damage": [
        """
           Based on information box and header-content pair article given,
            extract the insured damage information associated with the {Event_Name}, along with supporting source sections from the article.
            The insured damage information can be splited into 2 parts,
            the first is the total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy,
            - "Total_Insured_Damage": "The total amount of insured damage and make sure the information extracted for this containing the keyword "insured" or "insurance".
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of insured damage in the article to present the total number of insured damage,
               and if no total number of insured damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Insured_Damage_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total insured damage. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
              the second is the specific instance of insured damage caused by the {Event_Name}, 
              do not aggregate the information on insured damage from different locations; 
              instead, retain the data exactly as presented in the original text,
               make sure to capture all locations with insured damage information,
               if multiple sentences mention the  insured damage information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
                retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
              - "Specific_Instance_Per_Administrative_Area_Insured_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the insured damage occurred, and no matter the insured damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'. "
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The amount of insured damage in the specific location/locations related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion')."
              - "Num_Unit": "The currency of the insured damage, like USD, EUR. "
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the insured damage amount has been adjusted for inflation; otherwise "No"."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the insured damage, if applicable."
              - "Annotation": "Cite the header name and sentences from the article provided where you find the information about the insured damage, time and locations if available. "
             Take your time to read the whole text provided by the user, ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. """
    ],
    "Damage": [
        """
            Based on information box and header-content pair article given,
            extract the economic damage information associated with the {Event_Name}, along with supporting source sections from the article.
            The economic damage information can be splited into 2 parts,
            the first is the total economic damage caused by the {Event_Name},
            - "Total_Damage": "The total amount of economic damage.
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of economic damage in the article to present the total number of economic damage,
               and if no total number of economic damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Damage_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total economic damage. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
              the second is the specific instance of economic damage caused by the {Event_Name},
               do not aggregate the information on economic damage from different locations;
                instead, retain the data exactly as presented in the original text, 
                make sure to capture all locations with economic damage information,
                if multiple sentences mention the economic damage information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
                 retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the economic damage occurred, and no matter the economic damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The amount of economic damage in the specific location/locations related to the {Event_Name}.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion')."
              - "Num_Unit": "The currency of the economic damage, like USD, EUR. "
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the economic damage amount has been adjusted for inflation; otherwise "No"."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the economic damage, if applicable."
              - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the economic damage, time and locations if available."

                 }}]
             Take your time to read the whole text provided by the user, ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. """
    ],


    "main_event_hazard": [
        """
         Based on information box and header-content pair article,
         extract main_event category and hazard information associated with the {Event_Name}, along with supporting source sections from the article.
         Below is the Main_Event--Hazard association table,
         Main Event: Flood; Hazard: Flood
         Main Event: Extratropical Storm/Cyclone; Hazards: Wind; Flood; Blizzard; Hail
         Main Event: Tropical Storm/Cyclone; Hazards: Wind; Flood; Lightning
         Main Event: Extreme Temperature; Hazards: Heatwave; Cold Spell
         Main Event: Drought; Hazard: Drought
         Main Event: Wildfire; Hazard: Wildfire
         Main Event: Tornado; Hazard: Wind
         first identify the Main_Event category information from the text, 
           - "Main_Event": "identify the event category of the {Event_Name} referring the Main_Event--Hazard table, and only one Main_Event category should be assigned."
           - "Main_Event_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the Main_Event category. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
         based on the result of the Main_Event category from the previous step and the Main_Event--Hazard table, identify the hazard information and organize this information in JSON format as follows:
           - "Hazards": "Identify the hazards of the {Event_Name}, make sure the hazards are associated with the Main_Event category from the table, and if more than one hazard is detected from the text, separate them with '|'. "
           - "Hazards_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the hazard information. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
        
        Take your time to read the whole text provided by the user, and answer the questions."""
    ],
    # in this version, we ask the model to extract all the affected locations in L1, but in the post-processing, only extract the countries in this field.
    "location_time": [
        """
        Based on information box and header-content pair article, extract time and location information associated with the {Event_Name}, along with supporting source sections from the article.
        the first is to identify the time information of the event {Event_Name}:
        - "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "Time_Annotation": "Cite "Info_Box" or the header name or the sentences from the article provided where you find the information about the time."
        the second is to identify all countries affected by {Event_Name}:
        - "Administrative_Areas": "List all countries mentioned in the text affected by {Event_Name}. The list should be formatted as ["country1", "country2"]."
        - "Administrative_Areas_Annotation":  "Cite "Info_Box" or the header name or the sentences from the article provided where you find the information about the affected countries."
         Take your time to read the whole text provided by the user, and answer the questions."""
    ],
}





# this is version for multi event article, because the content from multi event article are much shorter, so we join the prompt below together in one
V_7_1_m= f"""Based on the content given by the user,

       first, extract time and location information associated with the {Event_Name}, along with supporting citations from the article.
        the first is to identify the time information of the event {Event_Name}:
        - "Start_Date": "The start date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "End_Date": "The end date of the event. If the specific day or month is not known, include at least the year if it's available. If no time information is available, enter 'NULL'. If the exact date is not clear (e.g., "summer of 2021", "June 2020"), please retain the text as mentioned."
        - "Time_Annotation": "Cite the sentences from the article provided where you find the information about the time."
        the second is to identify all countries affected by {Event_Name}:
        - "Administrative_Areas": "List all countries mentioned in the text affected by {Event_Name}. The list should be formatted as ["country1", "country2"]."
        - "Administrative_Areas_Annotation":  "Cite the sentences from the article provided where you find the information about the affected countries."
         Take your time to read the whole text provided by the user, and answer the questions above.

         Next, extract main_event category and hazard information associated with the {Event_Name}, along with supporting citations from the article.
         Below is the Main_Event--Hazard association table,
         Main Event: Flood; Hazard: Flood
         Main Event: Extratropical Storm/Cyclone; Hazards: Wind; Flood; Blizzard; Hail
         Main Event: Tropical Storm/Cyclone; Hazards: Wind; Flood; Lightning
         Main Event: Extreme Temperature; Hazards: Heatwave; Cold Spell
         Main Event: Drought; Hazard: Drought
         Main Event: Wildfire; Hazard: Wildfire
         Main Event: Tornado; Hazard: Wind
         first identify the Main_Event category information from the text, 
           - "Main_Event": "identify the event category of the {Event_Name} referring the Main_Event--Hazard table, and only one Main_Event category should be assigned."
           - "Main_Event_Annotation": "Cite the setences from the article provided where you find the information about the Main_Event category."
         based on the result of the Main_Event category from the previous step and the Main_Event--Hazard table, identify the hazard information and organize this information in JSON format as follows:
           - "Hazards": "Identify the hazards of the {Event_Name}, make sure the hazards are associated with the Main_Event category from the table, and if more than one hazard is detected from the text, separate them with '|'. "
           - "Hazards_Annotation": "Cite the setences from the article provided where you find the information about the hazard information."
        
        Take your time to read the whole text provided by the user, and answer the questions above.
 
    
      Next, extract the number of affected people associated with the {Event_Name}, along with supporting citations from the article.
      The affected people information can be splited into 2 parts,
      the first is the total number of affected people caused by the {Event_Name}, 
      - "Total_Affected": "The total number of people who were affected, impacted, or influenced in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of affected people in the article to present the total number of affected people,
         and if no total number of affected people explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Affected_Annotation": "Cite the setences from the content provided where you find the information about the total affected people. "
    
      the second is the specific instance of affected people caused by the {Event_Name}, 
      do not aggregate the information on affected people from different locations; instead, 
      retain the data exactly as presented in the original text, 
      make sure to capture all locations with affected people information, 
      if multiple sentences mention the affected people information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
      retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
      - "Specific_Instance_Per_Administrative_Area_Affected":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the affected people located, and no matter the affected people are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'. "
      - "Start_Date": "The start date when the people were affected, if mentioned."
      - "End_Date":"The end date when the people were affected, if mentioned."
      - "Num": "The number of people who were affected, impacted, or influenced in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the setences from the article provided where you find the information about the affected people, time, and locations if available."
      }}] 
      Take your time to read the whole text provided by the user, ensure to capture all instances of affected people mentioned in the article, including direct and indirect causes. 
     

      Next, extract the number of damaged buildings associated with the {Event_Name},
      covering a wide range of building types such as structures, homes, houses, households, apartments, office buildings, retail stores, hotels, schools, hospitals, and more,
      along with supporting citations from the article. The number of damaged buildings information can be splited into 2 parts,
      the first is the total number of damaged buildings caused by the {Event_Name}, and organize this information in JSON format as follows:

      - "Total_Buildings_Damaged": "The total number of damaged buildings in the {Event_Name}.
          Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes").
          Do not sum the number of damaged buildings in the article to present the total number of damaged buildings,
          and if no total number of damaged buildings explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Buildings_Damaged_Annotation": "Cite the setences from the article provided where you find the information about the total number of damaged buildings."
   
      the second is the specific instance of damaged buildings caused by the {Event_Name}, 
      do not aggregate the information on damaged buildings from different locations; 
      instead, retain the data exactly as presented in the original text, 
      make sure to capture all locations with damaged buildings information,  
      if multiple sentences mention the buildings damaged information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
      retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
      - "Specific_Instance_Per_Administrative_Area_Buildings_Damaged":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place/places within the country where the damaged buildings occurred, and no matter the building damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'."
      - "Start_Date": "The start date when the damaged buildings occurred, if mentioned."
      - "End_Date":"The end date when the damaged buildings occurred, if mentioned."
      - "Num": "The number of damaged buildings in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., "hundreds of, "few houses", "several homes"). "
      - "Annotation": "Cite the sentences from the article provided where you find the information about the building damages, time and location if available. "
      }}]
       Take your time to read the whole text provided by the user, ensure to capture all instances of damaged buildings mentioned in the article, including direct and indirect causes.  

   
      Next, extract the number of deaths associated with the {Event_Name},
      along with supporting citations from the article. The death information can be splited into 2 parts,
      the first is the total number of deaths caused by the {Event_Name}, 
      - "Total_Deaths": "The total number of people who died in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of death in the article to present the total number of death, and if no total number of death explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Deaths_Annotation": "Cite the setences from the article provided where you find the information about the total death."
      the second is the specific instance of deaths caused by the {Event_Name}, 
      do not aggregate the information on deaths from different locations; 
      instead, retain the data exactly as presented in the original text,
       make sure to capture all locations with death information,
       if multiple sentences mention the deaths information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
      retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
      - "Specific_Instance_Per_Administrative_Area_Deaths":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the deaths occurred, and no matter the deaths are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'."
      - "Start_Date": "The start date when the deaths occurred, if mentioned."
      - "End_Date":"The end date when the deaths occurred, if mentioned."
      - "Num": "The number of people who died in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). "
      - "Annotation": "Cite the sentences from the article provided where you find the information about the deaths, time and locations if available."
   }}]
       Take your time to read the whole text provided by the user, ensure to capture all instances of death mentioned in the article, including direct and indirect causes. 

 
      Next, extract the number of displacement associated with the {Event_Name}, along with supporting citations from the article.
      The displacement information can be splited into 2 parts,
      the first is the total number of displacement caused by the {Event_Name}, 
      - "Total_Displaced": "The total number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of displacement in the article to present the total number of displacement,
         and if no total number of displacement explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Displaced_Annotation": "Cite the setences from the article provided where you find the information about the total displacement."

      the second is the specific instance of displacement caused by the {Event_Name},
       do not aggregate the information on displacement from different locations; 
       instead, retain the data exactly as presented in the original text, 
       make sure to capture all locations with displacement information,
       if multiple sentences mention the displaced people information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
      retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
      - "Specific_Instance_Per_Administrative_Area_Displaced":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the displacement occurred, and no matter the displacement is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL"
      - "Start_Date": "The start date when the displacement occurred, if mentioned."
      - "End_Date":"The end date when the displacement occurred, if mentioned."
      - "Num": "The number of people who were displaced, evacuated, transfered/moved to the shelter, relocated or fleed in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people')."
      - "Annotation": "Cite the sentences from the article provided where you find the information about the displacement, time and locations. "
       }}]
       Take your time to read the whole text provided by the user, ensure to capture all instances of displacement mentioned in the article, including direct and indirect causes.  
   

  
       Next, extract the number of homelessness associated with the {Event_Name}, along with supporting citations from the article.
      The homelessness information can be splited into 2 parts,
      the first is the total number of homelessness caused by the {Event_Name}, 
      - "Total_Homeless": "The total number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of homelessness in the article to present the total number of homelessness,
         and if no total number of homelessness explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Homeless_Annotation": "Cite the setences from the article provided where you find the information about the total homelessness."
      
      the second is the specific instance of homelessness caused by the {Event_Name}, 
      do not aggregate the information on homelessness from different locations;
       instead, retain the data exactly as presented in the original text, 
       make sure to capture all locations with homelessness information,
       if multiple sentences mention the homeless people information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
      retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
      - "Specific_Instance_Per_Administrative_Area_Homeless":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the homelessness occurred, and no matter the homelessness is in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'."
      - "Start_Date": "The start date when the homelessness occurred, if mentioned."
      - "End_Date":"The end date when the homelessness occurred, if mentioned."
      - "Num": "The number of people who were homeless, lost their homes, experienced house damage, had their homes destroyed, were unhoused, without shelter, houseless, or shelterless in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). "
      - "Annotation": "Cite the sentences from the article provided where you find the information about the homelessness, time and location if available."
      }}]
       Take your time to read the whole text provided by the user, ensure to capture all instances of homelessness mentioned in the article, including direct and indirect causes.  
 

 
  
      Next, extract the number of non-fatal injuries associated with the {Event_Name}, along with supporting citations from the article.
      The non-fatal injuries information can be splited into 2 parts,
      the first is the total number of non-fatal injuries caused by the {Event_Name}, 
      - "Total_Injuries": "The total number of people who got injured, hurt, wound, or hospitalized (excluding death) in the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people').
         Do not sum the number of non-fatal injuries in the article to present the total number of non-fatal injuries,
         and if no total number of non-fatal injuries explicitly mentioned or the information is missing, assign 'NULL'."
      - "Total_Injuries_Annotation": "Cite the setences from the article provided where you find the information about the total non-fatal injuries."
      the second is the specific instance of non-fatal injuries caused by the {Event_Name}, 
      do not aggregate the information on injuries from different locations; 
      instead, retain the data exactly as presented in the original text, 
      make sure to capture all locations with non-fatal injuries information,
      if multiple sentences mention the non-fatal injuries information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
      retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
      - "Specific_Instance_Per_Administrative_Area_Injuries":[{{
      - "Administrative_Area": "Name of the country."
      - "Locations": "The specific place within the country where the non-fatal injuries occurred, and no matter the non-fatal injuries are in one or several places, order them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'. "
      - "Start_Date": "The start date when the non-fatal injuries occurred, if mentioned."
      - "End_Date":"The end date when the non-fatal injuries occurred, if mentioned."
      - "Num": "The number of people who got injured, hurt, wound, or hospitalized (excluding death) in the specific location/locations related to the {Event_Name}.
         Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundreds of,' '500 families,' 'at least 200', '300-500 people'). "
      - "Annotation": "Cite the sentences from the article provided where you find the information about the non-fatal injuries, time and locations if available. "
       }}]
       Take your time to read the whole text provided by the user, ensure to capture all instances of non-fatal injuries mentioned in the article, including direct and indirect causes. 

        
         Next, extract the insured damage information associated with the {Event_Name}, along with supporting citations from the article.
            The insured damage information can be splited into 2 parts,
            the first is the total insured damage caused by the {Event_Name}, including damage or loss to property, belongings, or persons covered under the terms of an insurance policy,
            - "Total_Insured_Damage": "The total amount of insured damage and make sure the information extracted for this containing the keyword "insured" or "insurance".
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of insured damage in the article to present the total number of insured damage,
               and if no total number of insured damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Insured_Damage_Unit": "The currency of the total insured damage, like USD, EUR; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total insured damage amount has been adjusted for inflation; otherwise "No", If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total insured damage, if applicable; If Total_Insured_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Insured_Damage_Annotation": "Cite the sentences from the article provided where you find the information about the total insured damage."
              the second is the specific instance of insured damage caused by the {Event_Name}, 
              do not aggregate the information on insured damage from different locations; 
              instead, retain the data exactly as presented in the original text,
               make sure to capture all locations with insured damage information,
               if multiple sentences mention the  insured damage information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
                retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
                
              - "Specific_Instance_Per_Administrative_Area_Insured_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the insured damage occurred, and no matter the insured damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'. "
              - "Start_Date": "The start date when the insured damage occurred, if mentioned."
              - "End_Date":"The end date when the insured damage occurred, if mentioned."
              - "Num": "The amount of insured damage in the specific location/locations related to the {Event_Name} and make sure the information extracted for this containing the keyword "insured" or "insurance".
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion')."
              - "Num_Unit": "The currency of the insured damage, like USD, EUR. "
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the insured damage amount has been adjusted for inflation; otherwise "No"."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the insured damage, if applicable."
              - "Annotation": "Cite sentences from the article provided where you find the information about the insured damage, time and locations if available. "
             }}]
             Take your time to read the whole text provided by the user, ensure to capture all instances of insured damage mentioned in the article, including direct and indirect causes. 
  
           
            Next, extract the economic damage information associated with the {Event_Name}, along with supporting source sections from the article.
            The economic damage information can be splited into 2 parts,
            the first is the total economic damage caused by the {Event_Name},
            - "Total_Damage": "The total amount of economic damage.
               Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion', "minimal").
               Do not sum the number of economic damage in the article to present the total number of economic damage,
               and if no total number of economic damage explicitly mentioned or the information is missing, assign 'NULL'."
            - "Total_Damage_Unit": "The currency of the total economic damage, like USD, EUR; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted": "Indicate 'Yes' if the total economic damage amount has been adjusted for inflation; otherwise "No", If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Inflation_Adjusted_Year": "The year of inflation adjustment for the total economic damage, if applicable; If Total_Economic_Damage is missing from the previous step, assign 'NULL'."
            - "Total_Damage_Annotation": "Cite "Info_Box" or the header name from the article provided where you find the information about the total economic damage. Besides, if the information is not from the Info_Box, cite the setences where you find the information."
              the second is the specific instance of economic damage caused by the {Event_Name},
               do not aggregate the information on economic damage from different locations;
                instead, retain the data exactly as presented in the original text, 
                make sure to capture all locations with economic damage information,
                if multiple sentences mention the economic damage information for the same location and same time (retain records separately if different time information is mentioned. If time is missing, consider it the same unless explicitly stated otherwise), 
                 retain all sentences in the 'Annotation' and use reasoning to select the most confirmed one.
             - "Specific_Instance_Per_Administrative_Area_Damage":[{{
              - "Administrative_Area": "Name of the country."
              - "Locations": "The specific place/places within the country where the economic damage occurred, and no matter the economic damage is in one or several places, order it/them in a list like ["Location1";"Location2";"Location3"]. If only the country name is available, leave this as 'NULL'."
              - "Start_Date": "The start date when the economic damage occurred, if mentioned."
              - "End_Date":"The end date when the economic damage occurred, if mentioned."
              - "Num": "The amount of economic damage in the specific location/locations related to the {Event_Name}.
                 Use the exact number if mentioned, or retain the text or range as provided for vague numbers (e.g., 'hundred million,''several billion')."
              - "Num_Unit": "The currency of the economic damage, like USD, EUR. "
              - "Num_Inflation_Adjusted": "Indicate 'Yes' if the economic damage amount has been adjusted for inflation; otherwise "No"."
              - "Num_Inflation_Adjusted_Year": "The year of inflation adjustment for the economic damage, if applicable."
              - "Annotation": "Cite the header name and the sentences from the article provided where you find the information about the economic damage, time and locations if available."

                 }}]
             Take your time to read the whole text provided by the user, ensure to capture all instances of economic damage mentioned in the article, including direct and indirect causes. 
    
      """
    

