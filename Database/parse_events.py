import argparse
import ast
import os
import re

import pandas as pd
import requests_cache
from dotenv import load_dotenv
from geopy.geocoders import Bing
from normalize_locs import NormalizeLoc
from normalize_nums import NormalizeNum, load_spacy_model

from Database.normalize_utils import NormalizeUtils as utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-sm",
        "--spaCy_model",
        dest="spaCy_model_name",
        default="en_core_web_trf",
        help="Choose a valid spaCy language model (https://spacy.io/models)",
        type=str,
    )
    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        default="response_wiki_GPT4_20240327_eventNo_1_8_all_category.json",
        help="The name of the json file in the <RAW_PATH> directory",
        type=str,
    )
    parser.add_argument(
        "-r",
        "--raw_path",
        dest="raw_path",
        default="Database/raw",
        help="The directory containing raw json files to be parsed",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output_path",
        dest="output_path",
        default="Database/output",
        help="The directory where the parsed events will land (as .parquet)",
        type=str,
    )
    parser.add_argument(
        "-l",
        "--locale",
        dest="locale_config",
        default="en_US.UTF-8",
        help="The locale encoding to localize numbers (eg. '32 000' -> `32000` or '1.000.000 (sv)' -> `1000000`). Run `import locale; locale.locale_alias` to get a full list of available locales",
        type=str,
    )

    parser.add_argument(
        "-t",
        "--event_type",
        dest="event_type",
        default="all",
        choices=["all", "main", "sub"],
        help="Choose which events to parse: main, sub, or all?",
        type=str,
    )
    args = parser.parse_args()
    nlp = load_spacy_model(args.spaCy_model_name)

    extract = NormalizeNum(nlp, locale_config=args.locale_config)

    requests_cache.install_cache("Database/data/geopy_cache")

    load_dotenv()

    api_key = os.getenv("BING_MAPS_API_KEY")
    geolocator = Bing(api_key=api_key, user_agent="shorouq.zahra@ri.se")
    norm_loc = NormalizeLoc(geolocator)

    df = pd.read_json(f"{args.raw_path}/{args.filename}")

    # add short uids for each event
    df["Event_ID"] = [utils.random_short_uuid() for _ in df.index]

    # unpack Total_Summary_* columns
    total_summary_cols = [col for col in df.columns if col.startswith("Total_")]
    events = utils.unpack_col(df, columns=total_summary_cols)

    del df
    if args.event_type in ["main", "all"]:
        # normalize dates
        if all([c in events.columns for c in ["Start_Date", "End_Date"]]):
            start_dates = events.Start_Date.apply(utils.normalize_date)
            end_dates = events.End_Date.apply(utils.normalize_date)

            start_date_cols = pd.DataFrame(
                start_dates.to_list(),
                columns=["Start_Date_Day", "Start_Date_Month", "Start_Date_Year"],
            )
            end_date_cols = pd.DataFrame(
                end_dates.to_list(), columns=["End_Date_Day", "End_Date_Month", "End_Date_Year"]
            )

            events = pd.concat([events, start_date_cols, end_date_cols], axis=1)
            del start_dates, end_dates, start_date_cols, end_date_cols

        # normalize binary categories into booleans
        _yes, _no = re.compile(r"^(yes)$|^(y)$|^(true)$", re.IGNORECASE | re.MULTILINE), re.compile(
            r"^(no)$|^(n)$|^(false)$", re.IGNORECASE | re.MULTILINE
        )

        if "Total_Insured_Damage_Inflation_Adjusted" in events.columns:
            events.Total_Insured_Damage_Inflation_Adjusted = events.Total_Insured_Damage_Inflation_Adjusted.replace(
                {_no: False, _yes: True}, regex=True
            )

        if "Total_Damage_Inflation_Adjusted" in events.columns:
            events.Total_Damage_Inflation_Adjusted = events.Total_Damage_Inflation_Adjusted.replace(
                {_no: False, _yes: True}, regex=True
            )
        # clean out NaNs and Nulls
        events = utils.replace_nulls(events)

        # get min, max, and approx numerals from relevant Total_* fields
        total_cols = [
            col
            for col in events.columns
            if col.startswith("Total_")
            and not col.endswith(("_with_annotation", "_Units", "_Year", "_Annotation", "_Adjusted"))
        ]
        for i in total_cols:
            events[[f"{i}_Min", f"{i}_Max", f"{i}_Approx"]] = (
                events[i]
                .apply(lambda x: (extract.extract_numbers(x) if x is not None else (None, None, None)))
                .apply(pd.Series)
            )

        # normalize Perils into a list
        if "Perils" in events.columns:
            events.Perils = events.Perils.apply(lambda x: x.split("|"))

        # normalize location names
        if "Country" in events.columns:
            events["Country_Norm"] = events.Country.apply(
                lambda countries: [norm_loc.normalize_locations(c) for c in countries] if countries else None
            )

        if "Location" in events.columns:
            events["Location_Norm"] = events.Location.apply(
                lambda locations: [norm_loc.normalize_locations(l) for l in locations] if locations else None
            )

        # clean out NaNs and Nulls
        events = utils.replace_nulls(events)

        annotation_cols = [col for col in events.columns if col.endswith(("_with_annotation", "_Annotation"))]

        for col in annotation_cols:
            events[col] = events[col].astype(str)

        # store as parquet and csv
        events_filename = f"{args.output_path}/{args.filename.split('.json')[0]}"
        events.to_parquet(f"{events_filename}.parquet")
        events.to_csv(f"{events_filename}.csv")

    if args.event_type in ["sub", "all"]:
        # parse subevents
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
            sub_event = utils.replace_nulls(sub_event)

            # get min, max, and approx nums from relevant Num_* & *Damage fields
            specific_total_cols = [
                col
                for col in sub_event.columns
                if col.startswith("Num_") or col.endswith("Damage") and "Date" not in col and "Location" not in col
            ]
            for i in specific_total_cols:
                sub_event[[f"{i}_Min", f"{i}_Max", f"{i}_Approx"]] = (
                    sub_event[i]
                    .apply(lambda x: (extract.extract_numbers(x) if x is not None else (None, None, None)))
                    .apply(pd.Series)
                )

            # clean out nulls after normalizing nums
            sub_event = utils.replace_nulls(sub_event)
            start_date_col, end_date_col = [c for c in sub_event.columns if c.startswith("Start_Date_")], [
                c for c in sub_event.columns if c.startswith("End_Date_")
            ]
            assert len(start_date_col) == len(end_date_col), "Check the start and end date columns"
            assert len(start_date_col) <= 1, "Check the start and end date columns, there might be too many"

            if start_date_col and end_date_col:
                start_date_col, end_date_col = start_date_col[0], end_date_col[0]

                # normalize start and end dates
                start_dates = sub_event[start_date_col].apply(utils.normalize_date)
                end_dates = sub_event[end_date_col].apply(utils.normalize_date)
                start_date_cols = pd.DataFrame(
                    start_dates.to_list(),
                    columns=[
                        f"{start_date_col}_Day",
                        f"{start_date_col}_Month",
                        f"{start_date_col}_Year",
                    ],
                )
                end_date_cols = pd.DataFrame(
                    end_dates.to_list(),
                    columns=[
                        f"{end_date_col}_Day",
                        f"{end_date_col}_Month",
                        f"{end_date_col}_Year",
                    ],
                )
                sub_event.reset_index(inplace=True, drop=True)
                sub_event = pd.concat([sub_event, start_date_cols, end_date_cols], axis=1)

            # normalize location names
            location_col = col.split("Specific_Instance_Per_Country_")[-1]

            sub_event["Country_Norm"] = sub_event["Country"].apply(
                lambda country: norm_loc.normalize_locations(country) if country else None
            )
            sub_event[f"Location_{location_col}_Norm"] = sub_event[f"Location_{location_col}"].apply(
                lambda location: norm_loc.normalize_locations(location) if location else None
            )

            # store as parquet and csv
            sub_event.to_parquet(f"{args.output_path}/{col}.parquet")
            sub_event.to_csv(f"{args.output_path}/{col}.csv")

        # TODO: fix annoying requests cache error
        # Traceback (most recent call last):
        # File "/Users/me/Library/Caches/pypoetry/virtualenvs/wikimpacts-1uvlbl-K-py3.11/lib/python3.11/site-packages/geopy/adapters.py", line 457, in __del__
        # File "/Users/me/Library/Caches/pypoetry/virtualenvs/wikimpacts-1uvlbl-K-py3.11/lib/python3.11/site-packages/requests_cache/session.py", line 341, in close
        # File "/Users/me/Library/Caches/pypoetry/virtualenvs/wikimpacts-1uvlbl-K-py3.11/lib/python3.11/site-packages/requests_cache/backends/base.py", line 114, in close
        # AttributeError: 'NoneType' object has no attribute 'debug'

    requests_cache.uninstall_cache()
