import pandas as pd
import shortuuid
from  dateutil.parser import parse
from datetime import datetime
import json 

pd.set_option("display.max_columns", 30)
pd.set_option("display.max_colwidth", 30)
pd.set_option("display.max_rows", None)

def random_short_uuid(x, length: int = 7):
    return shortuuid.ShortUUID().random(length=length)

def parse_basic_info(basic_series: pd.Series) -> pd.DataFrame:
    output = []
    for i in basic_series:
        entry = {}
        for x in range(len(i)):
            entry.update(json.loads(i[x]))
        output.append(entry)
    return pd.DataFrame(output)

# TODO: maybe return this without the fuzzy matching, this depends on how many funny dates there will be
# TODO: a problem for later, parse each part of the date individually
# might have to combine datetime with dateutil or maybe even modify the function

def normalize_dates(row) -> datetime: # tuple[datetime, tuple]:
    if row is not None:
        dt = parse(str(row), fuzzy_with_tokens=False)
        return dt.strftime("%d-%m-%Y")
    return None

def parse_json(x):
    try:
        return json.loads(x)
    except json.JSONDecodeError as err:
        print("Skipping parsing for:\n", x)
        print(err)
        return {"Could not parse": str(x)}
    
def flatten_dicts(json_dict_list: list[str]) -> dict:
    output = {}
    for i in json_dict_list:
        try:
            # i = json.loads(i) TODO: no need for this, already json dict
            for k in i.keys():
                if "summary" in k.lower():
                    for total_key, total_value in i[k].items():
                        total_value = None if (isinstance(total_value, str) and total_value.lower() in ["null", "nan"]) else total_value
                        output.update({total_key: total_value})
        except BaseException as err:
            print("ERROR:", err, "Could not parse:\n", i, "\n")
    return output

if __name__  == "__main__":
    data_path = "Database/raw/response_wiki_GPT4_20240315_13events.json"
    df = pd.read_json(data_path)

    # add short uids for each event
    df["Event_ID"] = df["Event_Name"].apply(random_short_uuid)

    # parse basic info and add to flat table
    basic = parse_basic_info(df["basic"])
    data = pd.concat([df, basic], axis=1)
    data.drop(["basic"], axis=1, inplace=True)

    # remove "NULL" and "NAN" strings
    data.replace("NAN", None, inplace=True)
    data.replace("NULL", None, inplace=True)

    # normalize dates
    data.Start_Date = data.Start_Date.apply(normalize_dates)
    data.End_Date =  data.End_Date.apply(normalize_dates)
    data.Single_Date = data.Single_Date.apply(normalize_dates)


    # flatten impact totals
    impact_data = data[["Event_ID", "impact"]]
    impact_data = impact_data.explode("impact")

    impact_data.impact = impact_data.impact.apply(parse_json)

    total_rows = []
    
    for i in range(impact_data.Event_ID.nunique()):
        total_rows.append(flatten_dicts(impact_data.loc[i].impact.to_list()))

    print(total_rows)
    total_rows = pd.DataFrame(total_rows)
    flat_data = pd.concat([data, total_rows], axis=1)

    flat_data.Total_Insured_Damage_Inflation_Adjusted.replace({"No": False, "Yes": True}, inplace=True)
    flat_data.Total_Damage_Inflation_Adjusted.replace({"No": False, "Yes": True}, inplace=True)

    flat_data.drop("impact", inplace=True, axis=1)
    
    print(flat_data.columns)
    print(flat_data.shape)
    print(flat_data)

    # cast annotation fields as str
    flat_data = flat_data.astype(str)

    print(flat_data.dtypes)
    flat_data.to_parquet("Database/output/flat_basic_and_impact.parquet",)
    flat_data = pd.read_parquet("Database/output/flat_basic_and_impact.parquet")

    print(flat_data.dtypes)
