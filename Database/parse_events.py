import argparse
import ast
import re

import pandas as pd
from scr.normalize_locations import NormalizeLocation
from scr.normalize_numbers import NormalizeNumber
from scr.normalize_utils import NormalizeUtils as utils

if __name__ == "__main__":
    logger = utils.get_logger("parse_events")
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
    logger.info(f"Passed args: {args}")

    nlp = utils.load_spacy_model(args.spaCy_model_name)

    norm_num = NormalizeNumber(nlp, locale_config=args.locale_config)

    norm_loc = NormalizeLocation(
        gadm_path="Database/data/gadm_world.csv",
        unsd_path="Database/data/UNSD — Methodology.csv",
    )

    df = pd.read_json(f"{args.raw_path}/{args.filename}")
    logger.info("JSON datafile loaded")

    # add short uids for each event
    df["Event_ID"] = [utils.random_short_uuid() for _ in df.index]

    # unpack Total_Summary_* columns
    total_summary_cols = [col for col in df.columns if col.startswith("Total_")]
    events = utils.unpack_col(df, columns=total_summary_cols)
    logger.info(f"Total summary columns: {total_summary_cols}")

    del df

    if args.event_type in ["main", "all"]:
        # normalize dates
        if all([c in events.columns for c in ["Start_Date", "End_Date"]]):
            logger.info("Normalizing dates")
            start_dates = events.Start_Date.apply(utils.normalize_date)
            end_dates = events.End_Date.apply(utils.normalize_date)

            start_date_cols = pd.DataFrame(
                start_dates.to_list(),
                columns=["Start_Date_Day", "Start_Date_Month", "Start_Date_Year"],
            )
            end_date_cols = pd.DataFrame(
                end_dates.to_list(),
                columns=["End_Date_Day", "End_Date_Month", "End_Date_Year"],
            )
            events = pd.concat([events, start_date_cols, end_date_cols], axis=1)
            logger.info(f"Dropping columns with event year")
            events.dropna(subset=["Start_Date_Year", "End_Date_Year"], how="all", inplace=True)

            del start_dates, end_dates, start_date_cols, end_date_cols

        # normalize binary categories into booleans
        logger.info("Normalizing booleans")
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
        logger.info("Normalizing nulls")
        events = utils.replace_nulls(events)

        # get min, max, and approx numerals from relevant Total_* fields
        total_cols = [
            col
            for col in events.columns
            if col.startswith("Total_")
            and not col.endswith(("_with_annotation", "_Units", "_Year", "_Annotation", "_Adjusted"))
        ]
        logger.info(
            f"""Normalizing numbers to ranges and determining whether or
                    not they are an approximate (min, max, approx). Columns: {total_cols}"""
        )

        for i in total_cols:
            events[[f"{i}_Min", f"{i}_Max", f"{i}_Approx"]] = (
                events[i]
                .apply(lambda x: (norm_num.extract_numbers(x) if x is not None else (None, None, None)))
                .apply(pd.Series)
            )

        # normalize Perils into a list
        if "Perils" in events.columns:
            logger.info("Normalizing Perils to list")
            events.Perils = events.Perils.apply(lambda x: x.split("|"))

        # normalize location names
        if "Country" in events.columns:
            logger.info("Normalizing Countries")

            events["Country_Tmp"] = events["Country"].apply(
                lambda countries: [norm_loc.normalize_locations(c, is_country=True) for c in countries]
            )

            events[["Country_Norm", "Country_Type", "Country_GeoJson"]] = (
                events["Country_Tmp"]
                .apply(lambda x: ([i[0] for i in x], [i[1] for i in x], [i[2] for i in x]))
                .apply(pd.Series)
            )

            # TODO: Countries with no location can be searched again without the is_country flag
            events.drop(columns=["Country_Tmp"], inplace=True)

            logger.info("Getting GID from GADM for Countries")
            events["Country_GID"] = events["Country_Norm"].apply(
                lambda countries: (
                    [norm_loc.get_gadm_gid(country=c) if c else None for c in countries] if countries else None
                ),
            )

        if "Location" in events.columns and "Country" in events.columns:
            logger.info(f"Dropping columns with no country or sublocation")
            events.dropna(subset=["Location", "Country"], how="all", inplace=True)

            logger.info("Normalizing Locations")
            events["Location_Tmp"] = events["Location"].apply(
                lambda locations: (
                    [norm_loc.normalize_locations(area=area) for area in locations] if locations else None
                )
            )

            events[["Location_Norm", "Location_Type", "Location_GeoJson"]] = (
                events["Location_Tmp"]
                .apply(lambda x: ([i[0] for i in x], [i[1] for i in x], [i[2] for i in x]))
                .apply(pd.Series)
            )
            events.drop(columns=["Location_Tmp"], inplace=True)

            logger.info("Getting GID from GADM for Locations")

            events["Location_GID"] = events.apply(
                lambda row: (
                    [
                        # removes "countries" from the location column
                        # preserves order
                        # TODO: if location is added to main events, pass country param to get_gadm_gid func
                        (norm_loc.get_gadm_gid(area=area) if area not in row["Country_Norm"] else "COUNTRY")
                        for area in row["Location_Norm"]
                    ]
                    if row["Location_Norm"]
                    else None
                ),
                axis=1,
            )

            # removes "countries" from the location column
            # preserves order
            logger.info("Removing countries from normalized location list.")
            for loc_col in ["Location_Norm", "Location_Type", "Location_GeoJson"]:
                events[loc_col] = events.apply(
                    lambda row: [
                        row[loc_col][i] for i in range(len(row["Location_GID"])) if row["Location_GID"][i] != "COUNTRY"
                    ],
                    axis=1,
                )

            events["Location_GID"] = events["Location_GID"].apply(
                lambda locations: [l for l in locations if l != "COUNTRY"]
            )
        # clean out NaNs and Nulls
        logger.info("Normalizing nulls")
        events = utils.replace_nulls(events)

        logger.info("Converting annotation columns to strings to store in sqlite3")
        annotation_cols = [col for col in events.columns if col.endswith(("_with_annotation", "_Annotation"))]
        for col in annotation_cols:
            events[col] = events[col].astype(str)

        logger.info("Converting list columns to strings to store in sqlite3")
        for col in [
            "Perils",
            "Location",
            "Location_Norm",
            "Location_Type",
            "Location_GID",
            "Location_GeoJson",
            "Country",
            "Country_Norm",
            "Country_Type",
            "Country_GID",
            "Country_GeoJson",
        ]:
            if col in events.columns:
                events[col] = events[col].astype(str)

        # store as parquet and csv
        logger.info(f"Storing parsed results")
        events_filename = f"{args.output_path}/{args.filename.split('.json')[0]}"
        events.to_parquet(f"{events_filename}.parquet")
        events.to_csv(f"{events_filename}.csv")

    if args.event_type in ["sub", "all"]:
        # clean out NaNs and Nulls
        events = utils.replace_nulls(events)

        # parse subevents
        specific_summary_cols = [col for col in events if col.startswith("Specific_")]
        logger.info(f"Parsing suevenets. Columns: {specific_summary_cols}")
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
            logger.info(f"Normalizing nulls for subevent {col}")
            sub_event = utils.replace_nulls(sub_event)

            # get min, max, and approx nums from relevant Num_* & *Damage fields
            specific_total_cols = [
                col
                for col in sub_event.columns
                if col.startswith("Num_") or col.endswith("Damage") and "Date" not in col and "Location" not in col
            ]
            logger.info(
                f"""Normalizing numbers to ranges in subenet {col} and determining whether or not they are an approximate (min, max, approx). Columns: {specific_total_cols}"""
            )

            for i in specific_total_cols:
                sub_event[[f"{i}_Min", f"{i}_Max", f"{i}_Approx"]] = (
                    sub_event[i]
                    .apply(lambda x: (norm_num.extract_numbers(x) if x is not None else (None, None, None)))
                    .apply(pd.Series)
                )

            # clean out nulls after normalizing nums
            logger.info(f"Normalizing nulls for subevent {col}")
            sub_event = utils.replace_nulls(sub_event)

            logger.info(f"Normalizing dates for subevet {col}")
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

            logger.info(f"Normalizing country names for subevent {col}")

            sub_event[["Country_Norm", "Country_Type", "Country_GeoJson"]] = (
                sub_event["Country"]
                .apply(lambda country: norm_loc.normalize_locations(country, is_country=True))
                .apply(pd.Series)
            )

            logger.info(f"Getting GID from GADM for countries in subevent {col}")
            sub_event["Country_GID"] = sub_event["Country_Norm"].apply(
                lambda country: (norm_loc.get_gadm_gid(country=country) if country else None)
            )
            logger.info(f"Dropping columns with no locations for subevent {col}")
            sub_event.dropna(subset=[f"Location_{location_col}"], how="all", inplace=True)

            logger.info(f"Normalizing location names for subevent {col}")
            sub_event[
                [
                    f"Location_{location_col}_Norm",
                    f"Location_{location_col}_Type",
                    f"Location_{location_col}_GeoJson",
                ]
                # Sometimes, subevents can have a location and country that are the same
                # (meaning the sub-event occurred in the same country), so the right params
                # are passed to the function (it's better to search for locations with the advanced OSM query search)
            ] = sub_event.apply(
                lambda row: norm_loc.normalize_locations(
                    area=row[f"Location_{location_col}"], in_country=row["Country_Norm"]
                )
                if row[f"Location_{location_col}"] != row["Country_Norm"]
                else norm_loc.normalize_locations(area=row["Country_Norm"], is_country=True),
                axis=1,
            ).apply(
                pd.Series
            )

            logger.info(f"Getting GID from GADM for locations in subevent {col}")
            sub_event[f"Location_{location_col}_GID"] = sub_event.apply(
                lambda row: (
                    norm_loc.get_gadm_gid(
                        area=row[f"Location_{location_col}_Norm"],
                        country=row["Country_Norm"],
                    )
                    if row[f"Location_{location_col}_Norm"]
                    else None
                ),
                axis=1,
            )
            sub_event[f"Location_{location_col}_GID"] = sub_event[f"Location_{location_col}_GID"].astype(str)

            # store as parquet and csv
            logger.info(f"Storing parsed results for sunevent {col}")
            sub_event.to_parquet(f"{args.output_path}/{col}.parquet")
            sub_event.to_csv(f"{args.output_path}/{col}.csv")

    norm_loc.uninstall_cache()
