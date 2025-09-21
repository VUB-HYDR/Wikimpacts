import argparse
import pathlib
import re

import pandas as pd
from tqdm import tqdm

from Database.scr.log_utils import Logging
from Database.scr.normalize_locations import NormalizeLocation
from Database.scr.normalize_numbers import NormalizeNumber
from Database.scr.normalize_utils import CategoricalValidation, NormalizeUtils

tqdm.pandas()


def infer_countries(
    row: dict,
    admin_area_col: str,
) -> list:
    countries = []
    gids_list = row.get(f"{admin_area_col}_GID", [])

    if isinstance(gids_list, list):
        for gids in gids_list:
            if isinstance(gids, list) and gids:
                for gd in gids:
                    if isinstance(gd, str) and gd:
                        # Perform the split and check for length 3 before extending
                        split_value = gd.split(".")[0]
                        if len(split_value) == 3:
                            countries.append(split_value)

    countries = list(set(countries))

    return [norm_loc.get_gid_0(c) for c in countries if norm_loc.get_gid_0(c)]


def parse_main_events(df: pd.DataFrame, target_columns: list):
    admin_area_col = "Administrative_Areas"
    logger.info("STEP: Parsing main level events (l1)")

    if "Event_ID" not in df.columns:
        logger.info("Event ids missing... generating random short uuids for col Event_ID")
        df["Event_ID"] = [utils.random_short_uuid() for _ in df.index]
    logger.info("Unpacking Total_Summary_* columns")
    total_summary_cols = [col for col in df.columns if col.startswith("Total_Summary_")]
    for i in total_summary_cols:
        df[i] = df[i].progress_apply(utils.eval)
    events = utils.unpack_col(df, columns=total_summary_cols)
    logger.info(f"Total summary columns: {total_summary_cols}")
    del df

    if any([c in events.columns for c in ["Start_Date", "End_Date"]]):
        logger.info("STEP: Normalizing start and end dates if present")
        for d_col in ["Start_Date", "End_Date"]:
            logger.info(f"Normalizing date column: {d_col}")
            dates = events[d_col].progress_apply(utils.normalize_date)
            date_cols = pd.DataFrame(
                dates.to_list(),
                columns=[f"{d_col}_Day", f"{d_col}_Month", f"{d_col}_Year"],
            )
            events = pd.concat([events, date_cols], axis=1)
            del date_cols

    logger.info("STEP: Normalizing booleans if present")
    _yes, _no = re.compile(r"^(yes)$|^(y)$|^(true)$", re.IGNORECASE | re.MULTILINE), re.compile(
        r"^(no)$|^(n)$|^(false)$", re.IGNORECASE | re.MULTILINE
    )
    for inflation_adjusted_col in [col for col in events.columns if col.endswith("_Adjusted")]:
        logger.info(f"Normalizing boolean column {inflation_adjusted_col}")
        events[inflation_adjusted_col] = events[inflation_adjusted_col].progress_apply(
            lambda value: (
                True
                if value and not isinstance(value, bool) and re.match(_yes, value)
                else (False if value and not isinstance(value, bool) and re.match(_no, value) else value)
            )
            if not pd.isna(value)
            else None
        )
    logger.info("STEP: Normalizing nulls")
    events = utils.replace_nulls(events)

    total_cols = [
        col
        for col in events.columns
        if col.startswith("Total_")
        and not col.endswith(("_with_annotation", "_Unit", "_Year", "_Annotation", "_Adjusted"))
    ]

    logger.info(f"STEP: Normalizing ranges if present in {total_cols}")
    for i in total_cols:
        if i in events.columns:
            logger.info(f"Normalizing ranges in {i}")
            events[[f"{i}_Min", f"{i}_Max", f"{i}_Approx"]] = (
                events[i]
                .progress_apply(lambda x: (norm_num.extract_numbers(x) if isinstance(x, str) else (None, None, None)))
                .apply(pd.Series)
            )

    split_by_pipe_cols = ["Hazards"]
    for str_col in [x for x in events.columns if x in split_by_pipe_cols]:
        logger.info(f"Splitting column {str_col} by pipe")
        events[str_col] = events[str_col].progress_apply(
            lambda x: (x.split("|") if isinstance(x, str) else (x if isinstance(x, str) else []))
        )

    logger.info("STEP: Normalizing country-level administrative areas if present")

    if "Administrative_Areas" in events.columns:
        logger.info(f"Ensuring that all admin area data in Administrative_Areas is of type <list>")
        events["Administrative_Areas"] = events["Administrative_Areas"].progress_apply(
            lambda x: utils.eval(x) if x is not None else []
        )

        logger.info("Normalizing administrative areas...")
        events[f"{admin_area_col}_Tmp"] = events["Administrative_Areas"].progress_apply(
            lambda admin_areas: (
                [norm_loc.normalize_locations(area=c, is_country=True) for c in admin_areas]
                if isinstance(admin_areas, list)
                else []
            )
        )
        events[
            [
                f"{admin_area_col}_Norm",
                f"{admin_area_col}_Type",
                f"{admin_area_col}_GeoJson",
            ]
        ] = (
            events[f"{admin_area_col}_Tmp"]
            .progress_apply(
                lambda x: (
                    (
                        [i[0] for i in x],
                        [i[1] for i in x],
                        [i[2] for i in x],
                    )
                    if isinstance(x, list)
                    else ([], [], [])
                )
            )
            .apply(pd.Series)
        )

        events.drop(columns=[f"{admin_area_col}_Tmp"], inplace=True)
        logger.info("Getting GID from GADM for Administrative Areas")
        events[f"{admin_area_col}_GID"] = events[f"{admin_area_col}_Norm"].progress_apply(
            lambda admin_areas: (
                [
                    (
                        norm_loc.get_gadm_gid(country=area)
                        if norm_loc.get_gadm_gid(country=area)
                        else norm_loc.get_gadm_gid(area=area)
                    )
                    for area in admin_areas
                    if area
                ]
                if isinstance(admin_areas, list)
                else []
            ),
        )

        logger.info(f"""STEP: Infer country from list of locations""")

        events[f"{admin_area_col}_GID_0_Tmp"] = events.progress_apply(
            lambda x: infer_countries(x, admin_area_col=admin_area_col), axis=1
        )

        logger.info("Normalizing administrative areas after purging areas above GID_0 level...")

        events[f"{admin_area_col}_GID_0_Tmp"] = events[f"{admin_area_col}_GID_0_Tmp"].progress_apply(
            lambda admin_areas: (
                [norm_loc.normalize_locations(c, is_country=True) for c in admin_areas]
                if isinstance(admin_areas, list)
                else []
            )
        )

        events[
            [
                f"{admin_area_col}_Norm",
                f"{admin_area_col}_Type",
                f"{admin_area_col}_GeoJson",
            ]
        ] = (
            events[f"{admin_area_col}_GID_0_Tmp"]
            .progress_apply(
                lambda x: (
                    (
                        [i[0] for i in x],
                        [i[1] for i in x],
                        [i[2] for i in x],
                    )
                    if isinstance(x, list)
                    else ([], [], [])
                )
            )
            .apply(pd.Series)
        )

        events.drop(columns=[f"{admin_area_col}_GID_0_Tmp"], inplace=True)
        logger.info("Getting GID from GADM for Administrative Areas after purging areas above GID_0 level...")
        events[f"{admin_area_col}_GID"] = events[f"{admin_area_col}_Norm"].progress_apply(
            lambda admin_areas: (
                [
                    (
                        norm_loc.get_gadm_gid(country=area)
                        if norm_loc.get_gadm_gid(country=area)
                        else norm_loc.get_gadm_gid(area=area)
                    )
                    for area in admin_areas
                    if area
                ]
                if isinstance(admin_areas, list)
                else []
            ),
        )

    logger.info("STEP: Cleanup")
    logger.info("Normalizing nulls")
    events = utils.replace_nulls(events)
    logger.info("Cleaning event names...")
    event_name_col = [x for x in events.columns if "Event_Name" in x]
    if len(event_name_col) == 1:
        event_name_col_str: str = event_name_col[0]
        events["Event_Names"] = events[event_name_col_str].progress_apply(
            lambda x: ([x.strip()] if isinstance(x, str) else ([y.strip() for y in x]) if isinstance(x, list) else [])
        )

    hazards, main_event = "Hazards", "Main_Event"
    if hazards in events.columns:
        logger.info(f"STEP: Validation of Categorical Types for col {hazards}")
        events[hazards] = events[hazards].apply(
            lambda hazard_list: [
                y
                for y in [
                    validation.validate_categorical(h, categories=validation.hazards_categories) for h in hazard_list
                ]
                if y
            ]
            if hazard_list
            else None
        )

    if main_event in events.columns:
        logger.info(f"STEP: Validation of Categorical Types for col {main_event}")
        events[main_event] = events[main_event].progress_apply(
            lambda main_event_type: validation.validate_categorical(
                main_event_type, categories=list(validation.main_event_categories.keys())
            )
        )
    if all([x in events.columns for x in [hazards, main_event]]):
        logger.info(f"STEP: Validation relationship between col {hazards} and col {main_event}")
        events = events.progress_apply(lambda row: validation.validate_main_event_hazard_relation(row), axis=1)

    logger.info(f"Storing parsed results for l1 events. Target columns: {target_columns}")
    utils.df_to_parquet(
        events[[x for x in target_columns if x in events.columns]],
        f"{args.output_dir}/l1",
        200,
    )
    del total_summary_cols, total_cols
    return events


def parse_sub_level_event(df, level: str, target_columns: list = []):
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

        logger.info(f"STEP: Parsing level {level} with column prefix {column_pattern}")
    except AssertionError as err:
        logger.error(
            f"Level {level} unavailable. Available levels: {list(available_subevent_levels.keys())}. Error: {err}"
        )
        raise AssertionError

    logger.info("STEP: Normalizing nulls and NaNs")
    df = utils.replace_nulls(df)

    specific_summary_cols = [col for col in df if col.startswith(column_pattern)]
    logger.info(f"STEP: Parsing {level}. Columns: {specific_summary_cols}")

    for col in specific_summary_cols:
        # evaluate string bytes to python datatype (hopefully dict, str, or list)
        df[col] = df[col].progress_apply(utils.eval)

        # unpack subevents
        sub_event = df[["Event_ID", col]].explode(col)

        # drop any events that have no subevents (aka [] exploded into NaN)
        sub_event.dropna(how="all", inplace=True)
        sub_event = pd.concat([sub_event.Event_ID, sub_event[col].apply(pd.Series)], axis=1)

        logger.info(
            f"Dropping any columns with non-str column names due to None types in the dicts {[c for c in sub_event.columns if not isinstance(c, str)]}"
        )
        sub_event = sub_event[[c for c in sub_event.columns if isinstance(c, str)]]

        # ignore empty categories
        if sub_event.empty:
            logger.warning(f"No data found in {col}! Level: {level}")
        elif sub_event.shape[1] < 2:
            logger.warning(f"No data found in {col}! Level: {level}")
        else:
            logger.info(f"Normalizing nulls for {level} {col}")
            sub_event = utils.replace_nulls(sub_event)

            specific_total_cols = [
                # keep as list in case more are added in the future
                col
                for col in sub_event.columns
                if col == "Num"
            ]
            if specific_total_cols:
                logger.info(
                    f"""Normalizing numbers to ranges in {level} {col} and determining whether or not they are an approximate (min, max, approx). Columns: {specific_total_cols}"""
                )
                for i in specific_total_cols:
                    sub_event[[f"{i}_Min", f"{i}_Max", f"{i}_Approx"]] = (
                        sub_event[i]
                        .progress_apply(
                            lambda x: (norm_num.extract_numbers(str(x)) if x is not None else (None, None, None))
                        )
                        .apply(pd.Series)
                    )
            logger.info(f"Normalizing nulls for {level} {col}")
            sub_event = utils.replace_nulls(sub_event)

        _yes, _no = re.compile(r"^(yes)$|^(y)$|^(true)$", re.IGNORECASE | re.MULTILINE), re.compile(
            r"^(no)$|^(n)$|^(false)$", re.IGNORECASE | re.MULTILINE
        )
        for inflation_adjusted_col in [col for col in sub_event.columns if col.endswith("_Adjusted")]:
            logger.info(f"Normalizing boolean column {inflation_adjusted_col} for {level} {col}")
            sub_event[inflation_adjusted_col] = sub_event[inflation_adjusted_col].progress_apply(
                lambda value: (
                    True
                    if value and not isinstance(value, bool) and re.match(_yes, value)
                    else (False if value and not isinstance(value, bool) and re.match(_no, value) else value)
                )
            )
        logger.info(f"Normalizing dates for subevet {col}")
        start_date_col, end_date_col = (
            "Start_Date" if "Start_Date" in sub_event.columns else None,
            "End_Date" if "End_Date" in sub_event.columns else None,
        )
        concat_list = [sub_event]
        if start_date_col:
            logger.info(f"Normalizing start date column {start_date_col}")
            start_dates = sub_event[start_date_col].progress_apply(utils.normalize_date)
            start_date_cols = pd.DataFrame(
                start_dates.to_list(),
                columns=[
                    f"{start_date_col}_Day",
                    f"{start_date_col}_Month",
                    f"{start_date_col}_Year",
                ],
            )
            concat_list.append(start_date_cols)

        if start_date_col:
            logger.info(f"Normalizing end date column {end_date_col}")
            end_dates = sub_event[end_date_col].progress_apply(utils.normalize_date)
            end_date_cols = pd.DataFrame(
                end_dates.to_list(),
                columns=[
                    f"{end_date_col}_Day",
                    f"{end_date_col}_Month",
                    f"{end_date_col}_Year",
                ],
            )
            concat_list.append(end_date_cols)
        sub_event.reset_index(inplace=True, drop=True)
        sub_event = pd.concat(concat_list, axis=1)
        del concat_list

        if level == "l2" and administrative_area_col in sub_event.columns:
            logger.info(f"Normalizing nulls in {administrative_area_col} for {level} {col}")
            sub_event[administrative_area_col] = sub_event[administrative_area_col].progress_apply(
                lambda admin_areas: utils.filter_null_list(admin_areas) if isinstance(admin_areas, list) else []
            )
            logger.info(f"Normalizing administrative area names for {level} {col}")
            sub_event[f"{administrative_area_col}_Tmp"] = sub_event[administrative_area_col].progress_apply(
                lambda admin_areas: (
                    [norm_loc.normalize_locations(c, is_country=True) for c in admin_areas]
                    if isinstance(admin_areas, list)
                    else []
                )
            )
            sub_event[
                [
                    f"{administrative_area_col}_Norm",
                    f"{administrative_area_col}_Type",
                    f"{administrative_area_col}_GeoJson",
                ]
            ] = (
                sub_event[f"{administrative_area_col}_Tmp"]
                .progress_apply(
                    lambda x: (
                        (
                            [i[0] for i in x],
                            [i[1] for i in x],
                            [i[2] for i in x],
                        )
                        if isinstance(x, list)
                        else ([], [], [])
                    )
                )
                .apply(pd.Series)
            )

            sub_event.drop(columns=[f"{administrative_area_col}_Tmp"], inplace=True)
            logger.info(f"Getting GID from GADM for Administrative Areas in {level} {col}")
            sub_event[f"{administrative_area_col}_GID"] = sub_event[f"{administrative_area_col}_Norm"].progress_apply(
                lambda admin_areas: (
                    [
                        (
                            norm_loc.get_gadm_gid(country=area)
                            if norm_loc.get_gadm_gid(country=area)
                            else norm_loc.get_gadm_gid(area=area)
                        )
                        for area in admin_areas
                        if area
                    ]
                    if isinstance(admin_areas, list)
                    else [[] for _ in admin_areas]
                ),
            )

        elif level == "l3" and administrative_area_col in sub_event.columns:
            logger.info(f"Normalizing nulls in {administrative_area_col} for {level} {col}")
            sub_event[administrative_area_col] = sub_event[administrative_area_col].apply(
                lambda admin_area: utils.filter_null_str(admin_area)
            )
            sub_event[
                [
                    f"{administrative_area_col}_Norm",
                    f"{administrative_area_col}_Type",
                    f"{administrative_area_col}_GeoJson",
                ]
            ] = (
                sub_event[administrative_area_col]
                .progress_apply(
                    lambda admin_area: (
                        norm_loc.normalize_locations(admin_area, is_country=True)
                        if isinstance(admin_area, str)
                        else (None, None, None)
                    )
                )
                .progress_apply(pd.Series)
            )
            logger.info(f"Getting GID from GADM for Administrative Areas in subevent {col}")

            sub_event[f"{administrative_area_col}_GID"] = sub_event[f"{administrative_area_col}_Norm"].progress_apply(
                lambda area: norm_loc.get_gadm_gid(country=area) if area else []
            )

            if location_col in sub_event.columns:
                logger.info(f"Normalizing nulls in {location_col} for {level} {col}")
                sub_event[location_col] = sub_event[location_col].progress_apply(
                    lambda locations: utils.filter_null_list(locations) if isinstance(locations, list) else []
                )
                logger.info(f"Normalizing location names for {level} {col}")
                sub_event[f"{location_col}_Tmp"] = sub_event.progress_apply(
                    lambda row: (
                        [
                            norm_loc.normalize_locations(
                                area=row[location_col][i],
                                in_country=row[f"{administrative_area_col}_Norm"],
                            )
                            for i in range(len(row[location_col]))
                        ]
                        if isinstance(row[location_col], list)
                        else []
                    ),
                    axis=1,
                )

                sub_event[
                    [
                        f"{location_col}_Norm",
                        f"{location_col}_Type",
                        f"{location_col}_GeoJson",
                    ]
                ] = (
                    sub_event[f"{location_col}_Tmp"]
                    .progress_apply(
                        lambda x: (
                            (
                                [i[0] for i in x],
                                [i[1] for i in x],
                                [i[2] for i in x],
                            )
                            if isinstance(x, list)
                            else ([], [], [])
                        )
                    )
                    .apply(pd.Series)
                )

                sub_event.drop(columns=[f"{location_col}_Tmp"], inplace=True)
                logger.info(f"Getting GID from GADM for locations in {level} {col}")

                sub_event[f"{location_col}_GID"] = sub_event.progress_apply(
                    lambda row: (
                        [
                            (
                                norm_loc.get_gadm_gid(area=row[f"{location_col}_Norm"][i])
                                if norm_loc.get_gadm_gid(area=row[f"{location_col}_Norm"][i])
                                else norm_loc.get_gadm_gid(country=row[f"{location_col}_Norm"][i])
                            )
                            if row[f"{location_col}_Norm"][i]
                            else []
                            for i in range(len(row[f"{location_col}_Norm"]))
                        ]
                    ),
                    axis=1,
                )
        logger.info(f"Dropping empty rows in {col}")
        rows_before = sub_event.shape[0]
        null_mask = (
            sub_event[[x for x in sub_event.columns if x != "Event_ID"]]
            .progress_apply(lambda row: [True if v in (None, [], float("nan")) else False for _, v in row.items()])
            .all(axis=1)
        )
        sub_event = sub_event[~null_mask]
        rows_after = sub_event.shape[0]
        logger.info(f"Dropped {rows_before-rows_after} row(s) in {col}")
        del rows_before, rows_after
        logger.info(f"Storing parsed results for subevent {col}")
        if target_columns:
            logger.info(f"Storing the following target columns for {col} {level}: {target_columns}")
            sub_event = sub_event[[x for x in target_columns if x in sub_event.columns]]
        logger.info(f"Normalizing nulls for {level} {col}")
        sub_event = utils.replace_nulls(sub_event)
        utils.df_to_parquet(
            sub_event, target_dir=f"{args.output_dir}/{level}/{col}", chunk_size=200, object_encoding="infer"
        )


def get_target_cols() -> tuple[list]:
    date_cols = [
        "Start_Date_Day",
        "Start_Date_Month",
        "Start_Date_Year",
        "End_Date_Day",
        "End_Date_Month",
        "End_Date_Year",
    ]

    event_breakdown_columns = {
        "numerical": {
            "Injuries": [
                "Injuries_Min",
                "Injuries_Max",
                "Injuries_Approx",
            ],
            "Deaths": ["Deaths_Min", "Deaths_Max", "Deaths_Approx"],
            "Displaced": ["Displaced_Min", "Displaced_Max", "Displaced_Approx"],
            "Homeless": ["Homeless_Min", "Homeless_Max", "Homeless_Approx"],
            "Buildings_Damaged": [
                "Buildings_Damaged_Min",
                "Buildings_Damaged_Max",
                "Buildings_Damaged_Approx",
            ],
            "Affected": ["Affected_Min", "Affected_Max", "Affected_Approx"],
        },
        "monetary": {
            "Insured_Damage": [
                "Insured_Damage_Min",
                "Insured_Damage_Max",
                "Insured_Damage_Approx",
                "Insured_Damage_Unit",
                "Insured_Damage_Inflation_Adjusted",
                "Insured_Damage_Inflation_Adjusted_Year",
            ],
            "Damage": [
                "Damage_Min",
                "Damage_Max",
                "Damage_Approx",
                "Damage_Unit",
                "Damage_Inflation_Adjusted",
                "Damage_Inflation_Adjusted_Year",
            ],
        },
    }

    l1_target_columns = [
        "Event_ID",
        "Hazards",
        "Main_Event",
        "Event_Names",
        "Sources",
        "Administrative_Areas_Norm",
        "Administrative_Areas_Type",
        "Administrative_Areas_GID",
        "Administrative_Areas_GeoJson",
    ]

    l1_target_columns.extend(date_cols)

    for cat in ["numerical", "monetary"]:
        impacts = event_breakdown_columns[cat].keys()
        for im in impacts:
            l1_target_columns.extend([f"Total_{x}" for x in event_breakdown_columns[cat][im]])

    basic_subevent_cols = [
        "Event_ID",
        "Hazards",
        "Num_Min",
        "Num_Max",
        "Num_Approx",
        "Num_Unit",
        "Num_Inflation_Adjusted",
        "Num_Inflation_Adjusted_Year",
    ]
    l2_target_columns = basic_subevent_cols.copy()
    l2_target_columns.extend(date_cols)
    l2_target_columns.extend(
        [
            "Administrative_Areas_Norm",
            "Administrative_Areas_Type",
            "Administrative_Areas_GID",
            "Administrative_Areas_GeoJson",
        ]
    )

    l3_target_columns = basic_subevent_cols.copy()
    l3_target_columns.extend(date_cols)
    l3_target_columns.extend(
        [
            "Administrative_Area_Norm",
            "Administrative_Area_Type",
            "Administrative_Area_GID",
            "Administrative_Area_GeoJson",
            "Locations_Norm",
            "Locations_Type",
            "Locations_GID",
            "Locations_GeoJson",
        ]
    )

    return l1_target_columns, l2_target_columns, l3_target_columns


if __name__ == "__main__":
    logger = Logging.get_logger("parse_events", level="INFO", filename="parse_events.log")
    available_event_levels = ["l1", "l2", "l3"]
    l1_target_columns, l2_target_columns, l3_target_columns = get_target_cols()

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
        "-lvl",
        "--event_levels",
        dest="event_levels",
        default=",".join(available_event_levels),
        help=f'Choose which events to parse (choices: {",".join(available_event_levels)}). Pass as string and sepatate each choice with a comma; example: "l1,l2". Irrelevant levels are ignored.',
        type=str,
    )
    parser.add_argument(
        "-rl1",
        "--raw_l1",
        dest="raw_l1",
        default=None,
        help="Pass a filename (.json) to store or retrieve the raw output from l1.",
        type=str,
    )

    parser.add_argument(
        "-srl1",
        "--store_raw_l1",
        action="store_true",
        help="Pass to store a raw file of l1 events in json",
        required=False,
    )

    args = parser.parse_args()
    args.event_levels = args.event_levels.split(",")
    assert all(
        [True if x in available_event_levels else False for x in args.event_levels]
    ), f"Event type not available: {[x for x in args.event_levels if x not in available_event_levels]}.\nAvailable types: {available_event_levels}"
    if args.store_raw_l1:
        assert (
            args.raw_l1
        ), "If the `--store_raw_l1` flag is set, the `--raw_l1` param must be passed to give the raw json output for l1 a filename!"

    logger.info(f"Passed args: {args}")

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    utils = NormalizeUtils()
    validation = CategoricalValidation()
    nlp = utils.load_spacy_model(args.spaCy_model_name)

    norm_num = NormalizeNumber(nlp, locale_config=args.locale_config)

    norm_loc = NormalizeLocation(
        gadm_path="Database/data/gadm_world.csv",
        unsd_path="Database/data/UNSD — Methodology.csv",
    )

    events = None
    tmp_dir = f"{args.output_dir}/tmp"

    if args.raw_l1:
        try:
            events = pd.read_json(f"{tmp_dir}/{args.raw_l1}")
            # TODO: literal eval!
            logger.info(f"Loaded events DataFrame from {args.raw_l1}")
        except BaseException as err:
            logger.error(f"Cannot find {args.raw_l1}. Error: {err}.")

    if "l1" in args.event_levels:
        if events is None:
            df = pd.read_json(f"{args.raw_dir}/{args.filename}")
            logger.info("JSON datafile loaded")
            events = parse_main_events(df, l1_target_columns)
        if args.store_raw_l1 and args.raw_l1:
            # store raw events to extract l2 and l3 without having to reparse l1
            pathlib.Path(tmp_dir).mkdir(parents=True, exist_ok=True)
            events.to_json(f"{tmp_dir}/{args.raw_l1}", orient="records")
            logger.info(f"Raw events file stored in {tmp_dir}/{args.raw_l1}")

    target_cols_by_level = {"l2": l2_target_columns, "l3": l3_target_columns}
    for lvl in target_cols_by_level.keys():
        if events is not None and lvl in args.event_levels:
            parse_sub_level_event(events, lvl, target_columns=target_cols_by_level[lvl])
        else:
            if lvl in args.event_levels:
                logger.error(f"Could not parse level {lvl}")

    logger.info("PARSING COMPLETE")
