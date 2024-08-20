import argparse
import pathlib
import re

import pandas as pd

from Database.scr.normalize_locations import NormalizeLocation
from Database.scr.normalize_numbers import NormalizeNumber
from Database.scr.normalize_utils import Logging, NormalizeUtils

if __name__ == "__main__":
    logger = Logging.get_logger("parse_events")
    available_event_types = ["main", "specific_instance_per_country", "impact_per_country"]
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
        help="The name of the json file in the <raw_dir> directory",
        type=str,
    )
    parser.add_argument(
        "-r",
        "--raw_dir",
        dest="raw_dir",
        help="The directory containing raw json files to be parsed",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
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
        default="main,specific_instance_per_country,impact_per_country",
        help=f'Choose which events to parse (choices: {",".join(available_event_types)}). Pass as string and sepatate each choice with a comma; example: "main,impact_per_country". Irrelevant texts are ignored.',
        type=list,
    )

    parser.add_argument(
        "-con",
        "--administrative_area_column",
        dest="administrative_area_column",
        default="Administrative_Area",
        help="Name of the column containing a list of aministrative areas -- will be renamed to Administrative_Area_* after parsing",
        type=str,
    )

    parser.add_argument(
        "-loc",
        "--location_column",
        dest="location_column",
        default="Location",
        help="Name of the column containing a list of locations smaller than a 'country-level' administrative area -- will be renamed to Location_* after parsing",
        type=str,
    )

    args = parser.parse_args()
    args.event_type = args.event_type.split(",")
    assert any([x for x in args.event_type if x in available_event_types])
    logger.info(f"Passed args: {args}")

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    def normalize_location_rows_if_country(row):
        # TODO: what was this doing again? I think this needs to change after the latest changes to the structure
        # if location and admin area are identical in subevents, generalize admin area normalization
        if row[args.location_column] == row[args.administrative_area]:
            for i in ["Norm", "Type", "GeoJson", "GID"]:
                row["Location_{i}"] = row[f"Administrative_Area_{i}"]
            return row
        else:
            return row

    def parse_sub_level_event(column_pattern: str):
        """
        Parses sub-level events (events of a type smaller than "Main Event").
        column_pattern (str): the prefix of the column.  (eg. "Specific_" to capture sperific instance events per adminstrative areas).
        administrative_area_column_type (type): the type of the data in the administrative area column (str or list).
        has_location_column (bool): False to ignore the Location column -- the location column is assumed to be of type list[list[str|GeoJson]].
        """
        # clean out NaNs and Nulls
        events = utils.replace_nulls(events)

        # parse subevents
        specific_summary_cols = [col for col in events if col.startswith(column_pattern)]
        logger.info(f"Parsing subevents. Columns: {specific_summary_cols}")

        for col in specific_summary_cols:
            # evaluate string bytes to python datatype (hopefully dict, str, or list)
            events[col] = events[col].apply(utils.eval)

            # unpack subevents
            sub_event = events[["Event_ID", col]].explode(col)

            # drop any events that have no subevents (aka [] exploded into NaN)
            sub_event.dropna(how="all", inplace=True)

            sub_event = pd.concat([sub_event.Event_ID, sub_event[col].apply(pd.Series)], axis=1)

            logger.info(
                f"Dropping any columns with non-str column names due to None types in the dicts {[c for c in sub_event.columns if not isinstance(c, str)]}"
            )
            sub_event = sub_event[[c for c in sub_event.columns if isinstance(c, str)]]

            logger.info(f"Normalizing nulls for subevent {col}")
            sub_event = utils.replace_nulls(sub_event)

            specific_total_cols = [
                col
                for col in sub_event.columns
                if col.startswith("Num_")
                or col.endswith("Damage")
                and "Date" not in col
                and args.location_column not in col
            ]

            if specific_total_cols:
                logger.info(
                    f"""Normalizing numbers to ranges in subevent {col} and determining whether or not they are an approximate (min, max, approx). Columns: {specific_total_cols}"""
                )

                for i in specific_total_cols:
                    sub_event[[f"{i}_Min", f"{i}_Max", f"{i}_Approx"]] = (
                        sub_event[i]
                        .apply(lambda x: (norm_num.extract_numbers(str(x)) if x is not None else (None, None, None)))
                        .apply(pd.Series)
                    )

            logger.info(f"Normalizing nulls for subevent {col}")
            sub_event = utils.replace_nulls(sub_event)

            logger.info(f"Normalizing dates for subevet {col}")
            start_date_col, end_date_col = [col for col in sub_event.columns if col.startswith("Start_Date_")], [
                col for col in sub_event.columns if col.startswith("End_Date_")
            ]
            assert len(start_date_col) == len(end_date_col), "Check the start and end date columns"
            assert len(start_date_col) <= 1, "Check the start and end date columns, there might be too many"

            if start_date_col and end_date_col:
                logger.info(f"Normalizing start and end date in columns {start_date_col} and {end_date_col}")
                start_date_col, end_date_col = start_date_col[0], end_date_col[0]

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

            logger.info(f"Normalizing administrative area names for subevent {col}")

            sub_event[["Administrative_Area_Norm", "Administrative_Area_Type", "Administrative_Area_GeoJson"]] = (
                sub_event[args.administrative_area]
                .apply(lambda admin_area: norm_loc.normalize_locations(admin_area, is_country=True))
                .apply(pd.Series)
            )

            logger.info(f"Getting GID from GADM for Administrative Areas in subevent {col}")
            sub_event["Administrative_Area_GID"] = sub_event["Administrative_Area_Norm"].apply(
                lambda admin_area: (norm_loc.get_gadm_gid(country=admin_area) if admin_area else None)
            )

            """
            logger.info(f"Dropping columns with no locations for subevent {col}")
            sub_event.dropna(subset=[f"Location"], how="all", inplace=True)
            """
            logger.info(f"Normalizing location names for subevent {col}")
            sub_event[
                [
                    "Location_Norm",
                    "Location_Type",
                    "Location_GeoJson",
                ]
                # Sometimes, subevents can have a location and admin area that are the same
                # (meaning the sub-event occurred in the same admin area), so the right params
                # are passed to the function (it's better to search for locations with the advanced OSM query search)
            ] = sub_event.apply(
                lambda row: norm_loc.normalize_locations(
                    area=row[f"Location"], in_country=row["Administrative_Area_Norm"]
                )
                if row[f"Location"] != row["Administrative_Area_Norm"]
                else norm_loc.normalize_locations(area=row["Administrative_Area_Norm"], is_country=True),
                axis=1,
            ).apply(
                pd.Series
            )
            logger.info(f"Getting GID from GADM for locations in subevent {col}")
            sub_event[f"Location_GID"] = sub_event.apply(
                lambda row: (
                    norm_loc.get_gadm_gid(
                        area=row[f"Location_Norm"],
                        country=row["Administrative_Area_Norm"],
                    )
                    if row[f"Location_Norm"]
                    else None
                ),
                axis=1,
            )

            logger.info(
                "Cleaning locations and administrative areas that are identical (a subevent where the smallest location is a country-level admin area)"
            )
            sub_event = sub_event.apply(lambda row: normalize_location_rows_if_country(row), axis=1)

            sub_event["Location_GID"] = sub_event["Location_GID"].astype(str)
            sub_event["Administrative_Area_GID"] = sub_event["Administrative_Area_GID"].astype(str)

            sub_event[
                [
                    "Location_Norm",
                    "Location_Type",
                    "Location_GeoJson",
                ]
            ] = sub_event[
                [
                    "Location_Norm",
                    "Location_Type",
                    "Location_GeoJson",
                ]
            ].astype(str)

            if "Death_with_annotation" in sub_event.columns:
                sub_event["Death_with_annotation"] = sub_event["Death_with_annotation"].astype(str)

            logger.info(f"Storing parsed results for sunbvent {col}")

            for c in sub_event.columns:
                sub_event[c] = sub_event[c].astype(str)

            sub_event.to_parquet(f"{args.output_dir}/{col}.parquet", engine="fastparquet")

    utils = NormalizeUtils()
    nlp = utils.load_spacy_model(args.spaCy_model_name)

    norm_num = NormalizeNumber(nlp, locale_config=args.locale_config)

    norm_loc = NormalizeLocation(
        gadm_path="Database/data/gadm_world.csv",
        unsd_path="Database/data/UNSD — Methodology.csv",
    )

    df = pd.read_json(f"{args.raw_dir}/{args.filename}")
    logger.info("JSON datafile loaded")

    # add short uids for each event if missing
    if "Event_ID" not in df.columns:
        logger.info("Event ids missing... generating random short uuids for col Event_ID")
        df["Event_ID"] = [utils.random_short_uuid() for _ in df.index]

    # unpack Total_Summary_* columns
    total_summary_cols = [col for col in df.columns if col.startswith("Total_")]
    for i in total_summary_cols:
        df[i] = df[i].apply(utils.eval)
    events = utils.unpack_col(df, columns=total_summary_cols)
    logger.info(f"Total summary columns: {total_summary_cols}")

    del df

    if any([x for x in args.event_type if x in available_event_types]):
        if all([c in events.columns for c in ["Start_Date", "End_Date"]]):
            logger.info("Normalizing dates for main events")
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

            del start_dates, end_dates, start_date_cols, end_date_cols

        # normalize binary categories into booleans
        logger.info("Normalizing booleans")
        _yes, _no = re.compile(r"^(yes)$|^(y)$|^(true)$", re.IGNORECASE | re.MULTILINE), re.compile(
            r"^(no)$|^(n)$|^(false)$", re.IGNORECASE | re.MULTILINE
        )

        for inflation_adjusted_col in [col for col in events.columns if col.endswith("_Inflation_Adjusted")]:
            logger.info(f"Normalizing boolean column {inflation_adjusted_col}")
            events[inflation_adjusted_col] = events[inflation_adjusted_col].replace(
                {_no: False, _yes: True}, regex=True
            )

        logger.info("Normalizing nulls")
        events = utils.replace_nulls(events)

        total_cols = [
            col
            for col in events.columns
            if col.startswith("Total_")
            and not col.endswith(("_with_annotation", "_Units", "_Year", "_Annotation", "_Adjusted"))
        ]

        if total_cols:
            logger.info(
                f"""Normalizing numbers to ranges and determining whether or
                        not they are an approximate (min, max, approx). Columns: {total_cols}"""
            )

            for i in total_cols:
                events[[f"{i}_Min", f"{i}_Max", f"{i}_Approx"]] = (
                    events[i]
                    .apply(lambda x: (norm_num.extract_numbers(x) if isinstance(x, str) else (None, None, None)))
                    .apply(pd.Series)
                )

        if "Hazard" in events.columns:
            logger.info("Normalizing Hazard to list")
            events.Hazard = events.Hazard.apply(lambda x: x.split("|"))

        if args.administrative_area in events.columns:
            logger.info("Ensuring that all admin area data is of type <list>")

            events[args.administrative_area] = events[args.administrative_area].apply(
                lambda x: utils.eval(x) if x is not None else []
            )

            logger.info(f"Removing non-country areas from country column {args.administrative_area}")
            events[args.administrative_area] = events[args.administrative_area].apply(
                lambda admin_areas: [c for c in admin_areas if utils.simple_country_check(c)] if admin_areas else []
            )

            logger.info("Normalizing Administrative_Areas")
            events["Administrative_Area_Tmp"] = events[args.administrative_area].apply(
                lambda admin_areas: [norm_loc.normalize_locations(c, is_country=True) for c in admin_areas]
                if admin_areas
                else []
            )

            events[["Administrative_Area_Norm", "Administrative_Area_Type", "Administrative_Area_GeoJson"]] = (
                events["Administrative_Area_Tmp"]
                .apply(lambda x: ([i[0] for i in x], [i[1] for i in x], [i[2] for i in x]))
                .apply(pd.Series)
            )

            # TODO: Administrative Areas with no location can be searched again without the is_country flag
            events.drop(columns=["Administrative_Area_Tmp"], inplace=True)

            logger.info("Getting GID from GADM for Administrative Areas")
            events["Administrative_Area_GID"] = events["Administrative_Area_Norm"].apply(
                lambda admin_areas: (
                    [norm_loc.get_gadm_gid(country=c) if c else None for c in admin_areas] if admin_areas else None
                ),
            )

        if args.location_column in events.columns and args.administrative_area in events.columns:
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
                        # removes "Administrative Areas" from the location column
                        # preserves order
                        # TODO: if location is added to main events, pass country param to get_gadm_gid func
                        (norm_loc.get_gadm_gid(area=area) if area not in row["Administrative_Area_Norm"] else "COUNTRY")
                        for area in row["Location_Norm"]
                    ]
                    if row["Location_Norm"]
                    else None
                ),
                axis=1,
            )

            # removes "Administrative Areas" from the location column
            # preserves order
            logger.info("Removing Administrative Areas from normalized location list.")
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
        logger.info("Normalizing nulls")
        events = utils.replace_nulls(events)

        logger.info("Converting annotation columns to strings to store in sqlite3")
        annotation_cols = [col for col in events.columns if col.endswith(("_with_annotation", "_Annotation"))]
        for col in annotation_cols:
            events[col] = events[col].astype(str)

        logger.info("Converting list columns to strings to store in sqlite3")

        col_to_str = [
            "Hazard",
            args.location_column,
            "Location_Norm",
            "Location_Type",
            "Location_GID",
            "Location_GeoJson",
            args.administrative_area,
            "Administrative_Area_Norm",
            "Administrative_Area_Type",
            "Administrative_Area_GID",
            "Administrative_Area_GeoJson",
            "Total_Deaths",
            "Total_Damage",
            "Total_Hoemless",
            "Total_Buildings_Damaged",
            "Total_Damage_Inflation_Adjusted",
            "Total_Damage_Inflation_Adjusted_Year",
        ]
        col_to_str.extend([col for col in events if col.startswith("Specific_")])

        for col in col_to_str:
            if col in events.columns:
                events[col] = events[col].astype(str)

        for i in ["Administrative Areas_Affected"]:
            if i in events.columns:
                logger.info(f"Dropping unwanted column {i}")
                events.drop(columns=[i], inplace=True)

        logger.info(f"Storing parsed results")
        events_filename = f"{args.output_dir}/{args.filename.split('.json')[0]}"
        events.to_parquet(f"{events_filename}.parquet", engine="fastparquet")

    if args.event_type in ["sub", "all"]:
        pass
    norm_loc.uninstall_cache()
