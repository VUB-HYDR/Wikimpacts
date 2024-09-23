default_weights = {
    "l1": {
        "Event_ID": 0,
        "Main_Event": 1,
        "Event_Names": 0,
        "Hazards": 1,
        # Deaths
        "Total_Deaths_Min": 1,
        "Total_Deaths_Max": 1,
        # Injuries
        "Total_Injuries_Max": 1,
        "Total_Injuries_Min": 1,
        # Buildings Damaged
        "Total_Buildings_Damaged_Min": 1,
        "Total_Buildings_Damaged_Max": 1,
        # Affected
        "Total_Affected_Min": 1,
        "Total_Affected_Max": 1,
        # Homeless
        "Total_Homeless_Min": 1,
        "Total_Homeless_Max": 1,
        # Displaced
        "Total_Displaced_Min": 1,
        "Total_Displaced_Max": 1,
        # Damage
        # "Total_Damage_Min": 1,
        # "Total_Damage_Max": 1,
        # "Total_Damage_Unit": 1,
        # "Total_Damage_Inflation_Adjusted": 1,
        # "Total_Damage_Inflation_Adjusted_Year": 1,
        # Insured Damage
        # "Total_Insured_Damage_Min": 1,
        # "Total_Insured_Damage_Max": 1,
        # "Total_Insured_Damage_Unit": 1,
        # "Total_Insured_Damage_Inflation_Adjusted": 1,
        # "Total_Insured_Damage_Inflation_Adjusted_Year": 1,
        # Date
        "Start_Date_Day": 1,
        "Start_Date_Month": 1,
        "Start_Date_Year": 1,
        "End_Date_Day": 1,
        "End_Date_Month": 1,
        "End_Date_Year": 1,
        # Area
        "Administrative_Areas_Norm": 1,  # list
    },
    "l2_monetary": {
        "Event_ID": 0,
        # "Hazards": 1,
        # Date
        "Start_Date_Day": 1,
        "Start_Date_Month": 1,
        "Start_Date_Year": 1,
        "End_Date_Day": 1,
        "End_Date_Month": 1,
        "End_Date_Year": 1,
        # Area
        "Administrative_Areas_Norm": 1,  # list
        # Impact
        "Num_Min": 1,
        "Num_Max": 1,
        "Num_Unit": 1,
        "Num_Inflation_Adjusted": 1,
        "Num_Inflation_Adjusted_Year": 1,
    },
    "l2_numerical": {
        "Event_ID": 0,
        # "Hazards": 1,
        # Date
        "Start_Date_Day": 1,
        "Start_Date_Month": 1,
        "Start_Date_Year": 1,
        "End_Date_Day": 1,
        "End_Date_Month": 1,
        "End_Date_Year": 1,
        # Area
        "Administrative_Areas_Norm": 1,  # list
        # Impact
        "Num_Min": 1,
        "Num_Max": 1,
    },
    "l3_monetary": {
        "Event_ID": 0,
        # "Hazards": 1,
        # Date
        "Start_Date_Day": 1,
        "Start_Date_Month": 1,
        "Start_Date_Year": 1,
        "End_Date_Day": 1,
        "End_Date_Month": 1,
        "End_Date_Year": 1,
        # Area
        "Administrative_Area_Norm": 1,  # str
        "Locations_Norm": 1,  # list
        # Impact
        "Num_Min": 1,
        "Num_Max": 1,
        "Num_Unit": 1,
        "Num_Inflation_Adjusted": 1,
        "Num_Inflation_Adjusted_Year": 1,
    },
    "l3_numerical": {
        "Event_ID": 0,
        # "Hazards": 1,
        # Date
        "Start_Date_Day": 1,
        "Start_Date_Month": 1,
        "Start_Date_Year": 1,
        "End_Date_Day": 1,
        "End_Date_Month": 1,
        "End_Date_Year": 1,
        # Area
        "Administrative_Area_Norm": 1,  # str
        "Locations_Norm": 1,  # list
        # Impact
        "Num_Min": 1,
        "Num_Max": 1,
    },
}

weights = {
    "nlp4climate": {
        "Event_ID": 1,
        "Main_Event": 1,
        "Event_Name": 0,
        "Total_Deaths_Min": 1,
        "Total_Deaths_Max": 1,
        "Total_Damage_Min": 1,
        "Total_Damage_Max": 1,
        "Total_Damage_Units": 1,
        "Start_Date_Day": 1,
        "Start_Date_Month": 1,
        "Start_Date_Year": 1,
        "End_Date_Day": 1,
        "End_Date_Month": 1,
        "End_Date_Year": 1,
        "Country_Norm": 1,
    },
    "Homeless": {
        # Homeless
        "Event_ID": 0,
        "Total_Homeless_Min": 1,
        "Total_Homeless_Max": 1,
    },
    "ESSD_2024_l1": default_weights["l1"],  # default weights
    "ESSD_2024_l2_numerical": default_weights["l2_numerical"],  # default weights
    "ESSD_2024_l2_monetary": default_weights["l2_monetary"],  # default weights
    "ESSD_2024_l3_numerical": default_weights["l3_numerical"],  # default weights
    "ESSD_2024_l3_monetary": default_weights["l3_monetary"],  # default weights
}
