import pandas as pd
import shortuuid
from dateparser.date import DateDataParser
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
            try:
                entry.update(json.loads(i[x]))
            except BaseException as err:
                print(f"Parsing error\n{err}\n")
        output.append(entry)
    return pd.DataFrame(output)

# TODO: maybe return this without the fuzzy matching, this depends on how many funny dates there will be
# TODO: a problem for later, parse each part of the date individually
# might have to combine datetime with dateutil or maybe even modify the function

def normalize_date(row) -> tuple[int, int, int]: # tuple[datetime, tuple]:
    """
    See https://github.com/scrapinghub/dateparser/issues/700
    and https://dateparser.readthedocs.io/en/latest/dateparser.html#dateparser.date.DateDataParser.get_date_data

    Returns a tuple: (day, month, year) with None for missing values
    """
    if row is not None:
        # TODO: we assume we need at least a month and a year, talk to Ni about this
        ddp = DateDataParser(settings={
            "REQUIRE_PARTS": ["year"],
            "NORMALIZE": True,
            "PREFER_DATES_FROM": "past"})
        try:
            date = ddp.get_date_data(row)
            try: 
                date.date_obj.strftime("%Y-%m-%d")
            except: 
                return (None, None, None)
            
            if date.period == "year":
                return (None, None, date.date_obj.strftime("%Y"))

            elif date.period == "month":
                return (None, date.date_obj.strftime("%m"), date.date_obj.strftime("%Y"))
        
            elif date.period == "day":
                return (date.date_obj.strftime("%d"), date.date_obj.strftime("%m"), date.date_obj.strftime("%Y"))

        except BaseException as err:
            print(f"Date parsing error in {row} with date\n{err}\n")
            return (None, None, None)
        
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
    # data_path = "Database/raw/response_wiki_GPT4_20240315_13events.json"
    data_path = "Database/raw/response_wiki_GPT4_20240317_No1_79.json"
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
    Start_Dates = data.Start_Date.apply(normalize_date)
    End_Dates = data.End_Date.apply(normalize_date)

    Start_Date_Cols = pd.DataFrame(Start_Dates.to_list(), columns = ["Start_Date_Day", "Start_Date_Month", "Start_Date_Year"])
    End_Date_Cols = pd.DataFrame(End_Dates.to_list(), columns = ["End_Date_Day", "End_Date_Month", "End_Date_Year"])

    data = pd.concat([data, Start_Date_Cols, End_Date_Cols], axis=1)

    impact_data = data[["Event_ID", "impact"]]
    impact_data = impact_data.explode("impact")

    impact_data.impact = impact_data.impact.apply(parse_json)

    total_rows = []
    
    for i in range(impact_data.Event_ID.nunique()):
        total_rows.append(flatten_dicts(impact_data.loc[i].impact.to_list()))

    # print(total_rows)
    total_rows = pd.DataFrame(total_rows)
    flat_data = pd.concat([data, total_rows], axis=1)

    flat_data.Total_Insured_Damage_Inflation_Adjusted.replace({"No": False, "Yes": True}, inplace=True)
    flat_data.Total_Damage_Inflation_Adjusted.replace({"No": False, "Yes": True}, inplace=True)

    flat_data.drop("impact", inplace=True, axis=1)
    
    # print(flat_data.columns)
    # print(flat_data.shape)
    # print(flat_data)

    # cast annotation fields as str
    flat_data = flat_data.astype(str)

    # print(flat_data.dtypes)
    flat_data.to_parquet("Database/output/flat_basic_and_impact_79_dmy.parquet",)
    flat_data = pd.read_parquet("Database/output/flat_basic_and_impact_79_dmy.parquet")

