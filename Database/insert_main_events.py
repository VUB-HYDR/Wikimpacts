import sqlite3

import pandas as pd

if __name__ == "__main__":
    data_path = "Database/output"
    data = pd.read_parquet(f"{data_path}/response_wiki_GPT4_20240327_eventNo_1_8_all_category.parquet")
    data = data[
        [
            "Event_ID",
            "Event_Name",
            "Source",
            # "execution_time",
            "Main_Event",
            # "Main_Event_Assessment_With_Annotation",
            "Perils",
            # "Perils_Assessment_With_Annotation",
            "Location",
            # "Location_with_Annotation",
            "Country",
            # "Country_with_Annotation",
            # "Single_Date",
            "Start_Date_Day",
            "Start_Date_Month",
            "Start_Date_Year",
            "Start_Date",
            "End_Date_Day",
            "End_Date_Month",
            "End_Date_Year",
            "End_Date",
            # "Time_with_Annotation",
            "Total_Deaths",
            "Total_Deaths_Min",
            "Total_Deaths_Max",
            "Total_Deaths_Approx",
            # "Total_Death_Annotation",
            "Total_Injuries",
            "Total_Injuries_Min",
            "Total_Injuries_Max",
            "Total_Injuries_Approx",
            # "Total_Injuries_Annotation",
            "Total_Displacement",
            "Total_Displacement_Min",
            "Total_Displacement_Max",
            "Total_Displacement_Approx",
            # "Total_Displacement_Annotation",
            "Total_Homelessness",
            "Total_Homelessness_Min",
            "Total_Homelessness_Max",
            "Total_Homelessness_Approx",
            # "Total_Homelessness_Annotation",
            "Total_Insured_Damage",
            "Total_Insured_Damage_Min",
            "Total_Insured_Damage_Max",
            "Total_Insured_Damage_Approx",
            "Total_Insured_Damage_Units",
            "Total_Insured_Damage_Inflation_Adjusted",
            "Total_Insured_Damage_Inflation_Adjusted_Year",
            # "Total_Insured_Damage_Assessment_with_annotation",
            "Total_Damage",
            "Total_Damage_Min",
            "Total_Damage_Max",
            "Total_Damage_Approx",
            "Total_Damage_Units",
            "Total_Damage_Inflation_Adjusted",
            "Total_Damage_Inflation_Adjusted_Year",
            # "Economic_Impact_with_annotation",
            "Total_Buildings_Damage",
            "Total_Buildings_Damage_Min",
            "Total_Buildings_Damage_Max",
            "Total_Buildings_Damage_Approx",
            # "Total_Building_Damage_with_annotation"]
        ]
    ]

    connection = sqlite3.connect(f"{data_path}/impact.db")
    cursor = connection.cursor()

    # change if_exists to "append" to avoid overwriting the database
    # choose "replace" to overwrite the database with a fresh copy of the data
    data.to_sql("Events", con=connection, if_exists="replace", index=False)

    connection.close()
