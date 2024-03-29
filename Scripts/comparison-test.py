import comparer

if __name__ == "__main__":
    """Comparison test. Usage: python comparison-test.py"""

    v = {
        "Event_Type": "Drought",
        "Event_Name": None,
        "Insured_Damage_Units": "EUR",
        "Total_Damage_Units": None,
        "Location": "Mariehamn&Åland",
        "Single_Date": None,
        "Start_Date": "2022-10-12",
        "End_Date": "2022-10-30",
        "Total_Deaths": 0,
        "Num_Injured": 2,
        "Displaced_People": 2300,
        "Num_Homeless": 54,
        "Total_Affected": 102000,
        "Insured_Damage": 420000,
        "Insured_Damage_Inflation_Adjusted_Year": None,
        "Total_Damage": 500000,
        "Total_Damage_Inflation_Adjusted_Year": None,
        "Buildings_Damaged": 12,
        "Insured_Damage_Inflation_Adjusted": False,
        "Total_Damage_Inflation_Adjusted": False,
    }

    w = {
        "Event_Type": "Windstorm",
        "Event_Name": "Wanda",
        "Insured_Damage_Units": "USD",
        "Total_Damage_Units": None,
        "Location": "Eckerö&Åland",
        "Single_Date": None,
        "Start_Date": "2012-10-14",
        "End_Date": "2012-10-15",
        "Total_Deaths": 100,
        "Num_Injured": 22,
        "Displaced_People": 230,
        "Num_Homeless": 5,
        "Total_Affected": 10000,
        "Insured_Damage": 32000,
        "Insured_Damage_Inflation_Adjusted_Year": None,
        "Total_Damage": 60000,
        "Total_Damage_Inflation_Adjusted_Year": None,
        "Buildings_Damaged": 121,
        "Insured_Damage_Inflation_Adjusted": False,
        "Total_Damage_Inflation_Adjusted": False,
    }

    weights = {
        "Event_Type": 0,
        "Event_Name": 1,
        "Insured_Damage_Units": 1,
        "Total_Damage_Units": 1,
        "Location": 1,
        "Single_Date": 0,
        "Start_Date": 0.5,
        "End_Date": 0.5,
        "Total_Deaths": 1,
        "Num_Injured": 1,
        "Displaced_People": 0.3,
        "Num_Homeless": 0,
        "Total_Affected": 0,
        "Insured_Damage": 1,
        "Insured_Damage_Inflation_Adjusted_Year": 0,
        "Total_Damage": 0,
        "Total_Damage_Inflation_Adjusted_Year": 0,
        "Buildings_Damaged": 1,
        "Insured_Damage_Inflation_Adjusted": 0,
        "Total_Damage_Inflation_Adjusted": 0,
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
