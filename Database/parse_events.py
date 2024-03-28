import ast
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
    filename = "response_wiki_GPT4_20240327_eventNo_1_8_all_category.json"
    raw_path = "Database/raw"
    output_path = "Database/output"
    df = pd.read_json(f"{raw_path}/{filename}")

    # add short uids for each event
    df["Event_ID"] = [random_short_uuid() for _ in df.index]

    # unpack Total_Summary_* columns
    total_summary_cols = [col for col in df if col.startswith("Total_")]
    events = unpack_col(df, columns=total_summary_cols)

    del df
    # add short uids for each event
    # total_summary["Event_ID"] = random_short_uuid(length=7)

    # normalize dates
    start_dates = events.Start_Date.apply(normalize_date)
    end_dates = events.End_Date.apply(normalize_date)

    start_date_cols = pd.DataFrame(
        start_dates.to_list(),
        columns=["Start_Date_Day", "Start_Date_Month", "Start_Date_Year"],
    )
    end_date_cols = pd.DataFrame(end_dates.to_list(), columns=["End_Date_Day", "End_Date_Month", "End_Date_Year"])

    events = pd.concat([events, start_date_cols, end_date_cols], axis=1)
    del start_dates, end_dates, start_date_cols, end_date_cols

    # normalize binary categories into booleans
    _yes, _no = re.compile(r"^(yes)$|^(y)$|^(true)$", re.IGNORECASE | re.MULTILINE), re.compile(
        r"^(no)$|^(n)$|^(false)$", re.IGNORECASE | re.MULTILINE
    )

    events.Total_Insured_Damage_Inflation_Adjusted = events.Total_Insured_Damage_Inflation_Adjusted.replace(
        {_no: False, _yes: True}, regex=True
    )
    events.Total_Damage_Inflation_Adjusted = events.Total_Damage_Inflation_Adjusted.replace(
        {_no: False, _yes: True}, regex=True
    )

    # normalize Perils into a list
    events.Perils = events.Perils.apply(lambda x: x.split("|"))

    # clean out NaNs and Nulls
    events = replace_nulls(events)

    # convert to string bytes (for the Perils_Assessment_With_Annotation column)
    events = events.astype(str)

    # store as parquet
    events_parquet_filename = f"{output_path}/{filename.split('.json')[0]}.parquet"
    events.to_parquet(events_parquet_filename)

    specific_summary_cols = [col for col in events if col.startswith("Specific_")]
    specifc_summary_dfs = {}

    for col in specific_summary_cols:
        # evaluate string bytes to dict
        events[col] = events[col].astype(str)
        events[col] = events[col].apply(ast.literal_eval)

        # unpack subevents
        sub_event = events[["Event_ID", col]].explode(col)

        # drop any events that have no subevents (aka [] exploded into NaN)
        sub_event.dropna(inplace=True)
        sub_event = pd.concat([sub_event.Event_ID, sub_event[col].apply(pd.Series)], axis=1)

        # clean out nulls
        sub_event = replace_nulls(sub_event)

        # normalize start and end dates
        start_dates = sub_event.Start_Date.apply(normalize_date)
        end_dates = sub_event.End_Date.apply(normalize_date)

        start_date_cols = pd.DataFrame(
            start_dates.to_list(),
            columns=["Start_Date_Day", "Start_Date_Month", "Start_Date_Year"],
        )
        end_date_cols = pd.DataFrame(end_dates.to_list(), columns=["End_Date_Day", "End_Date_Month", "End_Date_Year"])

        sub_event = pd.concat([sub_event, start_date_cols, end_date_cols], axis=1)

        # store as parquet
        sub_event.to_parquet(f"{output_path}/{col}.parquet")
