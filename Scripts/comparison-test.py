import comparer

if __name__ == "__main__":
    """ Comparison test. Usage: python comparison-test.py """

    v = {"Event_Type": "Drought",
         "Event_Name": "Don",
         "Insured_Damage_Units": "EUR",
         "Total_Damage_Units": "EUR",
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
         "Total_Damage_Inflation_Adjusted": False}

    w = {"Event_Type": "Windstorm",
         "Event_Name": "Wanda",
         "Insured_Damage_Units": "USD",
         "Total_Damage_Units": "USD",
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
         "Total_Damage_Inflation_Adjusted": False}

    comp = comparer.Comparer()
    print("Individual scores:")
    for p in comp.all(v, w).items(): print(p)
    print("Average score:\n", comp.averaged(v, w))
