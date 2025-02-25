import comparer

if __name__ == "__main__":
    """Comparison test. Usage: python comparison-test.py"""

    v = {
        "Event_ID": "123",
        "Main_Event": "Drought",
        "Event_Name": None,
        "Total_Deaths_Min": 22,
        "Total_Deaths_Max": 26,
        "Total_Damage_Min": 6000000,
        "Total_Damage_Max": 6000000,
        "Total_Damage_Units": "USD",
        "Total_Damage_Inflation_Adjusted_Year": 2022,
        "Total_Damage_Inflation_Adjusted": False,
        "Start_Date_Day": 1,
        "Start_Date_Month": 1,
        "Start_Date_Year": 2022,
        "End_Date_Day": 7,
        "End_Date_Month": 1,
        "End_Date_Year": 2022,
        "Country_Norm": ["Macedonia", "Greece"],
    }

    w = {
        "Event_ID": "123",
        "Main_Event": "Windstorm",
        "Event_Name": "Wanda",
        "Total_Deaths_Min": 22,
        "Total_Deaths_Max": 26,
        "Total_Damage_Min": 6000000,
        "Total_Damage_Max": 6000000,
        "Total_Damage_Units": "USD",
        "Total_Damage_Inflation_Adjusted": True,
        "Total_Damage_Inflation_Adjusted_Year": 2023,
        "Start_Date_Day": None,
        "Start_Date_Month": 1,
        "Start_Date_Year": 2022,
        "End_Date_Day": 7,
        "End_Date_Month": 1,
        "End_Date_Year": 2022,
        "Country_Norm": ["Greece"],
    }

    weights = {
        "Main_Event": 1,
        "Event_Name": 0,
        "Total_Deaths_Min": 1,
        "Total_Deaths_Max": 1,
        "Total_Damage_Min": 1,
        "Total_Damage_Max": 1,
        "Total_Damage_Units": 1,
        "Total_Damage_Inflation_Adjusted": 1,
        "Total_Damage_Inflation_Adjusted_Year": 1,
        "Start_Date_Day": 1,
        "Start_Date_Month": 1,
        "Start_Date_Year": 1,
        "End_Date_Day": 7,
        "End_Date_Month": 1,
        "End_Date_Year": 1,
        "Country_Norm": 1,
    }

    null_penalty = 1

    comp = comparer.Comparer(null_penalty)
    print("Individual scores:")
    for p in comp.all(v, w).items():
        print(p)
    print("Weighted score:\n", comp.weighted(v, w, weights))
    p, r = comp.events([v, w], [w, w, w], weights)
    print("Precision:\n", p)
    print("Recall:\n", r)
