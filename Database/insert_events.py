import sqlite3
import pandas as pd


if __name__ == "__main__":
    connection = sqlite3.connect("Database/impact.db")
    cursor = connection.cursor()
    # run insert commands
    # data = pd.read_parquet("Database/output/flat_basic_and_impact.parquet")
    data = pd.read_parquet("Database/output/flat_basic_and_impact_79.parquet")

    data = data[[
        "Event_ID",
        "Event_Name",
        "Source",
        "execution_time",
        "Main_Event",
        # "Main_Event_Assessment_With_Annotation",
        "Perils",
        # "Perils_Assessment_With_Annotation",
        "Location",
        # "Location_with_Annotation",
        "Single_Date",
        "Start_Date",
        "End_Date",
        #"Time_with_Annotation",
        "Total_Deaths",
        #"Total_Death_Annotation",
        "Total_Injuries",
        #"Total_Injuries_Annotation",
        "Total_Displaced",
        #"Total_Displacement_Annotation",
        "Total_Homeless",
        #"Total_Homelessness_Annotation",
        "Total_Insured_Damage",
        "Total_Insured_Damage_Units",
        "Total_Insured_Damage_Inflation_Adjusted",
        "Total_Insured_Damage_Inflation_Adjusted_Year",
        # "Total_Insured_Damage_Assessment_with_annotation",
        "Total_Damage",
        "Total_Damage_Units",
        "Total_Damage_Inflation_Adjusted",
        "Total_Damage_Inflation_Adjusted_Year",
        #"Economic_Impact_with_annotation",
        "Total_Buildings_Damaged",
        #"Total_Building_Damage_with_annotation"]
        ]]
    
    # clean out any leftover nones, nans, nulls, etc
    data = data.replace({"nan": None, "NULL": None, "NaN": None, "null": None, "None": None})
    data = data.astype(object).where(pd.notnull(data), None)
    
    # instert into database
    # change if_exists to "append" to avoid overwriting the database
    data.to_sql("Events", con=connection, if_exists="replace", index=False)

    connection.close()