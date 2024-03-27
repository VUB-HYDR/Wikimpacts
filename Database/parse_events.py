import re

import pandas as pd
import shortuuid
from dateparser.date import DateDataParser

pd.set_option("display.max_columns", 30)
pd.set_option("display.max_colwidth", 30)
pd.set_option("display.max_rows", None)


def random_short_uuid(length: int = 7) -> str:
    """Generates a short alpha-numerical UID"""
    return shortuuid.ShortUUID().random(length=length)


def replace_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizes all variations of NULL, NaN, nan, null either as data types or as strings"""
    any_NULL = re.compile(r"^(null)$|^(nan)$", re.IGNORECASE | re.MULTILINE)
    df = df.replace(any_NULL, None)
    df = df.astype(object).where(pd.notnull(df), None)
    return df


def normalize_date(row: str | None) -> tuple[int, int, int]:
    """
    See https://github.com/scrapinghub/dateparser/issues/700
    and https://dateparser.readthedocs.io/en/latest/dateparser.html#dateparser.date.DateDataParser.get_date_data

    Returns a tuple: (day, month, year) with None for missing values
    """
    if row is not None:
        ddp = DateDataParser(
            settings={
                "REQUIRE_PARTS": ["year"],
                "NORMALIZE": True,
                "PREFER_DATES_FROM": "past",
            }
        )

        year, month, day = "%Y", "%m", "%d"

        try:
            date = ddp.get_date_data(row)
            try:
                date.date_obj.strftime("%Y-%m-%d")
            except:
                return (None, None, None)

            if date.period == "year":
                return (None, None, date.date_obj.strftime(year))

            elif date.period == "month":
                return (
                    None,
                    date.date_obj.strftime(month),
                    date.date_obj.strftime(year),
                )

            elif date.period == "day":
                return (
                    date.date_obj.strftime(day),
                    date.date_obj.strftime(month),
                    date.date_obj.strftime(year),
                )

        except BaseException as err:
            print(f"Date parsing error in {row} with date\n{err}\n")
            return (None, None, None)


def unpack_col(df: pd.DataFrame, columns: list = []) -> pd.DataFrame:
    """Unpacks Total_Summary_* columns"""
    for c in columns:
        df = pd.concat([pd.json_normalize(df[c]), df], axis=1)
        df.drop(columns=[c], inplace=True)
    return df


if __name__ == "__main__":
    # load raw file
    filename = "response_wiki_GPT4_20240320_test_hurricane_agnes.json"
    raw_path = "Database/raw"
    output_path = "Database/output"
    df = pd.read_json(f"{raw_path}/{filename}")

    # unpack total_summary columns
    total_summary_cols = [col for col in df if col.startswith("Total_")]
    total_summary = unpack_col(df, columns=total_summary_cols)

    # add short uids for each event
    total_summary["Event_ID"] = random_short_uuid(length=7)

    # normalize dates
    Start_Dates = total_summary.Start_Date.apply(normalize_date)
    End_Dates = total_summary.End_Date.apply(normalize_date)

    Start_Date_Cols = pd.DataFrame(
        Start_Dates.to_list(),
        columns=["Start_Date_Day", "Start_Date_Month", "Start_Date_Year"],
    )
    End_Date_Cols = pd.DataFrame(End_Dates.to_list(), columns=["End_Date_Day", "End_Date_Month", "End_Date_Year"])

    total_summary = pd.concat([total_summary, Start_Date_Cols, End_Date_Cols], axis=1)

    # normalize binary categories into booleans
    _yes, _no = re.compile(r"^(yes)$|^(y)$|^(true)$", re.IGNORECASE | re.MULTILINE), re.compile(
        r"^(no)$|^(n)$|^(false)$", re.IGNORECASE | re.MULTILINE
    )

    total_summary.Total_Insured_Damage_Inflation_Adjusted = (
        total_summary.Total_Insured_Damage_Inflation_Adjusted.replace({_no: False, _yes: True}, regex=True)
    )
    total_summary.Total_Damage_Inflation_Adjusted = total_summary.Total_Damage_Inflation_Adjusted.replace(
        {_no: False, _yes: True}, regex=True
    )

    # clean out NaNs and Nulls
    total_summary = replace_nulls(total_summary)

    total_summary_parquet_filename = f"{output_path}/{filename.split('.json')[0]}.parquet"
    total_summary.to_parquet(total_summary_parquet_filename)

    # get specific impact summaries
    specific_summary_cols = [col for col in total_summary if col.startswith("Specific_")]
    specifc_summary_dfs = {}

    # normalize the json columns to extract subevents tables
    for col in specific_summary_cols:
        assert df[col].shape == (1,), "Bad shape, not a list; check the data"
        normalized_df = pd.json_normalize(df[col][0])
        specifc_summary_dfs[col] = normalized_df

    # normalize dates (only for subevent data tables that have a Time_* field)
    specific_summary_with_dates = (
        ("Specific_Instance_Per_Country_Death", "Time_Death"),
        ("Specific_Instance_Per_Country_Injuries", "Time_Injuries"),
        ("Specific_Instance_Per_Country_Displacement", "Time_Displace"),
        ("Specific_Instance_Per_Country_Homelessness", "Time_Homeless"),
        ("Specific_Instance_Per_Country_Building_Damage", "Time_Building"),
    )

    for table_name, col_name in specific_summary_with_dates:
        date = specifc_summary_dfs[table_name][col_name].apply(normalize_date)
        date_col = pd.DataFrame(
            date.to_list(),
            columns=[f"{col_name}_Day", f"{col_name}_Month", f"{col_name}_Year"],
        )
        specifc_summary_dfs[table_name] = pd.concat([specifc_summary_dfs[table_name], date_col], axis=1)

    # store subevents in parquet
    for col_name, data in specifc_summary_dfs.items():
        data = replace_nulls(data)
        data.to_parquet(f"{output_path}/{col_name}.parquet")
