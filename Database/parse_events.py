import argparse
import os
import pathlib
import re

import pandas as pd
from tqdm import tqdm

from Database.scr.normalize_locations import NormalizeLocation
from Database.scr.normalize_numbers import NormalizeNumber
from Database.scr.normalize_utils import Logging, NormalizeUtils

tqdm.pandas()


def parse_main_events(df: pd.DataFrame, target_columns: list):
    logger.info("Step: Parsing main level events (L1)")

    if "Event_ID" not in df.columns:
        logger.info("Event ids missing... generating random short uuids for col Event_ID")
        df["Event_ID"] = [utils.random_short_uuid() for _ in df.index]

    logger.info("Unpacking Total_Summary_* columns")
    total_summary_cols = [col for col in df.columns if col.startswith("Total_")]
    for i in total_summary_cols:
        df[i] = df[i].progress_apply(utils.eval)
    events = utils.unpack_col(df, columns=total_summary_cols)

    logger.info(f"Total summary columns: {total_summary_cols}")
    del df

    if any([c in events.columns for c in ["Start_Date", "End_Date"]]):
        logger.info("Step: normalizing start and end dates if present")
        for d_col in ["Start_Date", "End_Date"]:
            logger.info(f"Normalizing date column: {d_col}")
            dates = events[d_col].progress_apply(utils.normalize_date)
            date_cols = pd.DataFrame(
                dates.to_list(),
                columns=[f"{d_col}_Day", f"{d_col}_Month", f"{d_col}_Year"],
            )
            events = pd.concat([events, date_cols], axis=1)
            del date_cols

    logger.info("Step: normalizing booleans if present")
    _yes, _no = re.compile(r"^(yes)$|^(y)$|^(true)$", re.IGNORECASE | re.MULTILINE), re.compile(
        r"^(no)$|^(n)$|^(false)$", re.IGNORECASE | re.MULTILINE
    )
    for inflation_adjusted_col in [col for col in events.columns if col.endswith("_Adjusted")]:
        logger.info(f"Normalizing boolean column {inflation_adjusted_col}")
        events[inflation_adjusted_col] = events[inflation_adjusted_col].replace({_no: False, _yes: True}, regex=True)
    logger.info("Step: normalizing nulls")
    events = utils.replace_nulls(events)
    total_cols = [
        col
        for col in events.columns
        if col.startswith("Total_")
        and not col.endswith(("_with_annotation", "_Unit", "_Year", "_Annotation", "_Adjusted"))
    ]

    logger.info("Step: normalizing ranges if present")
    if total_cols:
        for i in total_cols:
            if i in events.columns:
                logger.info(f"Normalizing ranges in {i}")
                events[[f"{i}_Min", f"{i}_Max", f"{i}_Approx"]] = (
                    events[i]
                    .progress_apply(
                        lambda x: (norm_num.extract_numbers(x) if isinstance(x, str) else (None, None, None))
                    )
                    .progress_apply(pd.Series)
                )

    logger.info("SPLIT COLUMNS BY PIPE IF PRESENT")
    for str_col in [x for x in events.columns if x in ["Hazards"]]:
        events[str_col] = events[str_col].progress_apply(
            lambda x: (x.split("|") if isinstance(x, str) else (x if isinstance(x, str) else None))
        )

    logger.info("Step: Normalizing country-level administrative areas if present")

    if "Administrative_Areas" in events.columns:
        logger.info(f"Ensuring that all admin area data in Administrative_Areas is of type <list>")
        events["Administrative_Areas"] = events["Administrative_Areas"].progress_apply(
            lambda x: utils.eval(x) if x is not None else []
        )

        logger.info("Normalizing administrative areas...")
        events["Administrative_Area_Tmp"] = events["Administrative_Areas"].progress_apply(
            lambda admin_areas: (
                [norm_loc.normalize_locations(c, is_country=True) for c in admin_areas] if admin_areas else []
            )
        )
        events[
            [
                "Administrative_Area_Norm",
                "Administrative_Area_Type",
                "Administrative_Area_GeoJson",
            ]
        ] = (
            events["Administrative_Area_Tmp"]
            .progress_apply(
                lambda x: (
                    [i[0] for i in x],
                    [i[1] for i in x],
                    [i[2] for i in x],
                )
            )
            .progress_apply(pd.Series)
        )

        # TODO: Administrative Areas with no location can be searched again without the is_country flag
        # TODO: change this when splitting the location function
        events.drop(columns=["Administrative_Area_Tmp"], inplace=True)
        logger.info("Getting GID from GADM for Administrative Areas")
        events["Administrative_Area_GID"] = events["Administrative_Area_Norm"].progress_apply(
            lambda admin_areas: (
                [norm_loc.get_gadm_gid(country=c) if c else None for c in admin_areas] if admin_areas else None
            ),
        )

    logger.info("Step: cleanup")
    logger.info("Normalizing nulls")
    events = utils.replace_nulls(events)
    logger.info("Converting annotation columns to strings to store in sqlite3")
    annotation_cols = [col for col in events.columns if col.endswith(("_with_annotation", "_Annotation"))]
    for col in annotation_cols:
        events[col] = events[col].astype(str)
    logger.info("Converting list columns to strings to store in sqlite3")

    for col in events.columns:
        events[col] = events[col].astype(str)

    logger.info(f"Storing parsed results for L1 events")
    df_to_parquet(events[[x for x in target_columns if x in events.columns]], args.output_dir, "Total_Summary", 200)
    del total_summary_cols, annotation_cols, total_cols
    return events


def parse_sub_level_event(level: str):
    available_subevent_levels = {
        "l2": {
            "prefix": "Instance",
            "administrative_area_col": "Administrative_Areas",
            "administrative_area_type": list,
            "location_col": None,
        },
        "l3": {
            "prefix": "Specific",
            "administrative_area_col": "Administrative_Area",
            "administrative_area_type": str,
            "location_col": "Locations",
        },
    }
    try:
        assert level in available_subevent_levels
        column_pattern = available_subevent_levels[level]["prefix"]
        administrative_area_col = available_subevent_levels[level]["administrative_area_col"]
        location_col = available_subevent_levels[level]["location_col"]

        logger.info(f"Parsing level {level} with column prefix {column_pattern}")
    except AssertionError as err:
        logger.error(
            f"Level {level} unavailable. Available subevent levels: {list(available_subevent_levels.keys())}. Error: {err}"
        )
        raise AssertionError

    logger.info("Normalizing nulls and NaNs")
    events = utils.replace_nulls(events)

    specific_summary_cols = [col for col in events if col.startswith(column_pattern)]
    logger.info(f"Parsing {level}. Columns: {specific_summary_cols}")

    for col in specific_summary_cols:
        # evaluate string bytes to python datatype (hopefully dict, str, or list)
        events[col] = events[col].progress_apply(utils.eval)

        # unpack subevents
        sub_event = events[["Event_ID", col]].explode(col)

        # drop any events that have no subevents (aka [] exploded into NaN)
        sub_event.dropna(how="all", inplace=True)
        sub_event = pd.concat([sub_event.Event_ID, sub_event[col].progress_apply(pd.Series)], axis=1)

        logger.info(
            f"Dropping any columns with non-str column names due to None types in the dicts {[c for c in sub_event.columns if not isinstance(c, str)]}"
        )
        sub_event = sub_event[[c for c in sub_event.columns if isinstance(c, str)]]

        logger.info(f"Normalizing nulls for subevent {col}")
        sub_event = utils.replace_nulls(sub_event)

        specific_total_cols = [
            col for col in sub_event.columns if col.startswith("Num_") and "Date" not in col and "Locations" not in col
        ]
        if specific_total_cols:
            logger.info(
                f"""Normalizing numbers to ranges in subevent {col} and determining whether or not they are an approximate (min, max, approx). Columns: {specific_total_cols}"""
            )
            for i in specific_total_cols:
                sub_event[[f"{i}_Min", f"{i}_Max", f"{i}_Approx"]] = (
                    sub_event[i]
                    .progress_apply(
                        lambda x: (norm_num.extract_numbers(str(x)) if x is not None else (None, None, None))
                    )
                    .progress_apply(pd.Series)
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
            start_dates = sub_event[start_date_col].progress_apply(utils.normalize_date)
            end_dates = sub_event[end_date_col].progress_apply(utils.normalize_date)
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

        if level == "l2":
            sub_event[
                [
                    f"{administrative_area_col}_Norm",
                    f"{administrative_area_col}_Type",
                    f"{administrative_area_col}_GeoJson",
                ]
            ] = (
                sub_event[administrative_area_col]
                .progress_apply(lambda admin_area: norm_loc.normalize_locations(admin_area, is_country=True))
                .progress_apply(pd.Series)
            )
            logger.info(f"Getting GID from GADM for Administrative Areas in subevent {col}")
            sub_event[f"{administrative_area_col}_GID"] = sub_event[f"{administrative_area_col}_Norm"].progress_apply(
                lambda admin_area: [norm_loc.normalize_locations(c, is_country=True) for c in admin_area]
                if isinstance(admin_area, available_subevent_levels[level]["administrative_area_type"])
                else []
            )

        elif level == "l3":
            sub_event[
                [
                    f"{administrative_area_col}_Norm",
                    f"{administrative_area_col}_Type",
                    f"{administrative_area_col}_GeoJson",
                ]
            ] = (
                sub_event[administrative_area_col]
                .progress_apply(
                    lambda admin_area: norm_loc.normalize_locations(admin_area, is_country=True)
                    if isinstance(admin_area, available_subevent_levels[level]["administrative_area_type"])
                    else None
                )
                .progress_apply(pd.Series)
            )
            logger.info(f"Getting GID from GADM for Administrative Areas in subevent {col}")
            sub_event[f"{administrative_area_col}_GID"] = sub_event[f"{administrative_area_col}_Norm"].progress_apply(
                lambda admin_area: (norm_loc.get_gadm_gid(country=admin_area) if admin_area else None)
            )
            logger.info(f"Normalizing location names for subevent {col}")
            sub_event[
                [
                    f"{location_col}_Norm",
                    f"{location_col}_Type",
                    f"{location_col}_GeoJson",
                ]
            ] = sub_event.progress_apply(
                lambda row: (
                    norm_loc.normalize_locations(
                        area=row[location_col], in_country=row[f"{administrative_area_col}_Norm"]
                    )
                    if isinstance(row[location_col], list)
                    else []
                ),
                axis=1,
            ).progress_apply(
                pd.Series
            )

            logger.info(f"Getting GID from GADM for locations in subevent {col}")

            sub_event[f"{location_col}_GID"] = sub_event.progress_apply(
                lambda row: (
                    [
                        norm_loc.get_gadm_gid(
                            area=row[f"{location_col}_Norm"][i],
                            country=row[f"{administrative_area_col}_Norm"],
                        )
                        for i in f"{location_col}_Norm"
                    ]
                    if isinstance(row[f"{location_col}_Norm"], list)
                    else None
                ),
                axis=1,
            )

        sub_event[f"{location_col}_GID"] = sub_event[f"{location_col}_GID"].astype(str)
        sub_event[f"{administrative_area_col}_GID"] = sub_event[f"{administrative_area_col}_GID"].astype(str)
        sub_event[
            [
                f"{location_col}_Norm",
                f"{location_col}_Type",
                f"{location_col}_GeoJson",
            ]
        ] = sub_event[
            [
                f"{location_col}_Norm",
                f"{location_col}_Type",
                f"{location_col}_GeoJson",
            ]
        ].astype(str)
        logger.info(f"Storing parsed results for sunbvent {col}")
        for c in sub_event.columns:
            sub_event[c] = sub_event[c].astype(str)
        df_to_parquet(
            target_dir=f"{args.output_dir}/{col}.parquet",
            target_file_prefix=available_subevent_levels[level]["prefix"],
            chunk_size=200,
            engine="fastparquet",
        )


def df_to_parquet(
    df: pd.DataFrame,
    target_dir: str,
    target_file_prefix: str,
    chunk_size: int = 2000,
    **parquet_wargs,
):
    """Writes pandas DataFrame to parquet format with pyarrow.
        Credit: https://stackoverflow.com/a/72010262/14123992
    Args:
        df: DataFrame
        target_dir: local directory where parquet files are written to
        chunk_size: number of rows stored in one chunk of parquet file. Defaults to 2000.
    """
    for i in range(0, len(df), chunk_size):
        slc = df.iloc[i : i + chunk_size]
        chunk = int(i / chunk_size)
        fname = os.path.join(target_dir, f"{target_file_prefix}_{chunk:04d}.parquet")
        slc.to_parquet(fname, engine="fastparquet", **parquet_wargs)


if __name__ == "__main__":
    logger = Logging.get_logger("parse_events", level="INFO")
    available_event_types = ["l1", "l2", "l3"]
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
        default=",".join(available_event_types),
        help=f'Choose which events to parse (choices: {",".join(available_event_types)}). Pass as string and sepatate each choice with a comma; example: "l1,l2". Irrelevant levels are ignored.',
        type=str,
    )

    event_breakdown_columns = {
        "numerical": {
            "Injuries": [
                "Injuries_Min",
                "Injuries_Max",
            ],
            "Deaths": [
                "Deaths_Min",
                "Deaths_Max",
            ],
            "Displaced": [
                "Displaced_Min",
                "Displaced_Max",
            ],
            "Homeless": [
                "Homeless_Min",
                "Homeless_Max",
            ],
            "Buildings_Damaged": [
                "Buildings_Damaged_Min",
                "Buildings_Damaged_Max",
            ],
            "Affected": ["Affected_Min", "Affected_Max"],
        },
        "monetary": {
            "Insured_Damage": [
                "Insured_Damage_Min",
                "Insured_Damage_Max",
                "Insured_Damage_Units",
                "Insured_Damage_Inflation_Adjusted",
                "Insured_Damage_Inflation_Adjusted_Year",
            ],
            "Damage": [
                "Damage_Min",
                "Damage_Max",
                "Damage_Units",
                "Damage_Inflation_Adjusted",
                "Damage_Inflation_Adjusted_Year",
            ],
        },
    }

    l1_target_columns = [
        "Event_ID",
        "Hazards",
        "Event_Name",
        "Source",
        "Administrative_Area_Norm",
        "Administrative_Area_Type",
        "Administrative_Area_GID",
        "Administrative_Area_GeoJson",
    ]
    l1_target_columns.extend([f"Total_{x}" for x in event_breakdown_columns["numerical"]])
    l1_target_columns.extend([f"Total_{x}" for x in event_breakdown_columns["monetary"]])

    args = parser.parse_args()
    args.event_type = args.event_type.split(",")
    assert all(
        [True if x in available_event_types else False for x in args.event_type]
    ), f"Event type not available: {[x for x in args.event_type if x not in available_event_types]}.\nAvailable types: {available_event_types}"
    logger.info(f"Passed args: {args}")

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    utils = NormalizeUtils()
    nlp = utils.load_spacy_model(args.spaCy_model_name)

    norm_num = NormalizeNumber(nlp, locale_config=args.locale_config)

    norm_loc = NormalizeLocation(
        gadm_path="Database/data/gadm_world.csv",
        unsd_path="Database/data/UNSD — Methodology.csv",
    )

    df = pd.read_json(f"{args.raw_dir}/{args.filename}")
    logger.info("JSON datafile loaded")

    if "l1" in args.event_type:
        parse_main_events(df, l1_target_columns)

    for lvl in ["l2", "l3"]:
        if lvl in args.event_type:
            # TODO: add target columns when saving
            parse_sub_level_event(lvl)

    norm_loc.uninstall_cache()
