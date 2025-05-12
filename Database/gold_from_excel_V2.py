import argparse
import pathlib
import re
from datetime import datetime

import pandas as pd
from tqdm import tqdm

from Database.scr.log_utils import Logging
from Database.scr.normalize_locations import NormalizeLocation
from Database.scr.normalize_utils import NormalizeUtils

tqdm.pandas()
utils = NormalizeUtils()


def flatten(xss):
    return [x for xs in xss for x in xs]


def fix_column_names(df):
    mapper = {
        "_Min": "Num_Min",
        "_Max": "Num_Max",
        "_Unit": "Num_Unit",
        "_Units": "Num_Unit",
        "_Adjusted": "Num_Inflation_Adjusted",
        "_Adjusted_Year": "Num_Inflation_Adjusted_Year",
    }

    for k, v in mapper.items():
        for col in df.columns:
            if col.endswith(k) and not col.startswith("Num_"):
                df.rename(columns={col: v}, inplace=True)
    return df


def _split_range(text: str) -> tuple[str | None, str | None]:
    r = text.split("-")
    if len(r) == 1:
        return (r[0], r[0])
    elif len(r) == 2:
        return r
    else:
        return (None, None)


## OUTPUT COLUMN SCHEMA ##

# set specific impact columns
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
            "Insured_Damage_Unit",
            "Insured_Damage_Inflation_Adjusted",
            "Insured_Damage_Inflation_Adjusted_Year",
        ],
        "Damage": [
            "Damage_Min",
            "Damage_Max",
            "Damage_Unit",
            "Damage_Inflation_Adjusted",
            "Damage_Inflation_Adjusted_Year",
        ],
    },
}

# l1, l2, and l3 have these three column sets in common
shared_cols = [
    "Event_ID",
    "Event_ID_decimal",
    "Sources",
    "Event_Names",
    "Main_Event",
    "Hazards",
    "split",  # dataset split; example: dev/test
]

location_cols = ["Administrative_Area_Norm", "Location_Norm","Locations_GID","Administrative_Area_GID"]

date_cols = [
    "Start_Date_Year",
    "Start_Date_Month",
    "Start_Date_Day",
    "End_Date_Year",
    "End_Date_Month",
    "End_Date_Day",
]

# set l1 output target columns
target_columns = flatten(
    [
        shared_cols,
        location_cols,
        date_cols,
        flatten([x for x in event_breakdown_columns["monetary"].values()]),
        flatten([x for x in event_breakdown_columns["numerical"].values()]),
    ]
)

## SETTINGS TO NORMALIZE COLUMNS ##

# get numerical type columns
numerical_type_col = []
for i in event_breakdown_columns["numerical"].keys():
    numerical_type_col.extend(event_breakdown_columns["numerical"][i])

# get string type columns
convert_to_str = flatten([shared_cols])
convert_to_int = flatten([date_cols, numerical_type_col])
convert_to_list = [
    "Sources",
    "Event_Names",
    "Hazards",
]

# get "list" type columns with pipe separator
split_by_pipe = ["Event_Names", "Sources", "Hazards"]
for i in event_breakdown_columns["monetary"].keys():
    split_by_pipe.append(i)
    split_by_pipe.extend(
        [x for x in event_breakdown_columns["monetary"][i] if not x.endswith("_Min") and not x.endswith("_Max")]
    )

# get bool type columns
convert_to_boolean = []
for i in event_breakdown_columns["monetary"].keys():
    convert_to_boolean.extend(
        [x for x in event_breakdown_columns["monetary"][i] if "_Adjusted" in x and "_Year" not in x]
    )

convert_to_float = ["Event_ID_decimal"]

# get monetary type columns
currency_unit_cols = []
for i in event_breakdown_columns["monetary"].keys():
    currency_unit_cols.extend([col for col in event_breakdown_columns["monetary"][i] if col.endswith("_Units")])


def flatten_data_table():
    logger.info(f"Loading excel file {args.input_file}, sheet {args.sheet_name}")
    data_table = pd.read_excel(args.input_file, sheet_name=args.sheet_name, engine="openpyxl", na_filter=False)
    logger.info(f"Shape before dropping blanks: {data_table.shape}")

    logger.info("Dropping blank cells if the entire row is missing...")
    data_table.dropna(
        how="all",
        inplace=True,
    )
    logger.info(f"Shape after dropping blanks: {data_table.shape}")

    logger.info("Normalizing all NULLs")
    null_pattern = re.compile(r"^[\s|.|,]*(null|nul)[\s|.|,]*$", flags=re.IGNORECASE | re.MULTILINE)
    for col in data_table.columns:
        data_table[col] = data_table[col].astype(str)
        data_table[col] = data_table[col].replace(null_pattern, None, regex=True)

    logger.info(f"Converting to integers: {convert_to_int}")
    for col in convert_to_int:
        logger.debug(f"Casting column {col} as int")
        if col in data_table.columns:
            data_table[col] = data_table[col].progress_apply(
                lambda x: (None if x is None else (int(x.strip()) if str(x).isdigit() else None))
            )
    data_table = data_table.replace(float("nan"), None)

    logger.info(f"Converting to strings: {convert_to_str}")
    for col in convert_to_str:
        logger.debug(col)
        data_table[col] = data_table[col].progress_apply(lambda x: None if x is None else str(x).strip())

    logger.info(f"Splitting by pipes: {split_by_pipe} and normalizing NULLs in the output lists")
    for col in split_by_pipe:
        logger.debug(f"Casting column {col} as list")
        data_table[col] = data_table[col].progress_apply(
            lambda x: [y for y in x.split("|")] if isinstance(x, str) else None
        )
        data_table[col] = data_table[col].progress_apply(
            lambda x: ([None if re.match(null_pattern, text) else text for text in x] if x else None)
        )
    logger.info(f"Validating Units for monetary type columns...")
    for col in currency_unit_cols:
        data_table[f"{col}_valid_currency"] = data_table[col].progress_apply(
            lambda x: all([utils.check_currency(y) for y in x]) if x else True
        )
        assert all(data_table[f"{col}_valid_currency"])
        data_table.drop(columns=[f"{col}_valid_currency"], inplace=True)

    logger.info(f"Validating Dates...")

    for col in date_cols:
        if col.endswith("Year"):
            data_table[f"{col}_valid_year"] = data_table[col].progress_apply(
                lambda x: (len(str(x).split(".")[0]) == 4 and x > 0 and x <= datetime.now().year if x else True)
            )
            assert all(data_table[f"{col}_valid_year"])
            data_table.drop(columns=[f"{col}_valid_year"], inplace=True)

        if col.endswith("Month"):
            data_table[f"{col}_valid_month"] = data_table[col].progress_apply(
                lambda x: x <= 12 and x > 0 if x else True
            )
            assert all(data_table[f"{col}_valid_month"])
            data_table.drop(columns=[f"{col}_valid_month"], inplace=True)

    for date_type in ["Start", "End"]:
        logger.info(f"Validating {date_type} date type")
        data_table[f"{date_type}_valid_date"] = data_table[
            [
                f"{date_type}_Date_Year",
                f"{date_type}_Date_Month",
                f"{date_type}_Date_Day",
            ]
        ].progress_apply(lambda x: utils.check_date(year=x[0], month=x[1], day=x[2]) if all(x) else True)

        assert all(data_table[f"{date_type}_valid_date"])
        data_table.drop(columns=[f"{date_type}_valid_date"], inplace=True)

    # ranges need to be extracted from monetary column types, but not from the numerical column types
    for col_type in event_breakdown_columns["monetary"].keys():
        logger.info(f"Normalizing ranges for {col_type}")

        data_table[f"{col_type}_Min"] = data_table[col_type].progress_apply(
            lambda x: [_split_range(y)[0] for y in x] if isinstance(x, list) else None
        )
        data_table[f"{col_type}_Max"] = data_table[col_type].progress_apply(
            lambda x: [_split_range(y)[1] for y in x] if isinstance(x, list) else None
        )

    logger.info(f"Converting to floats: {convert_to_float}")
    for col in convert_to_float:
        logger.debug(col)
        data_table[col] = data_table[col].progress_apply(lambda x: float(x) if isinstance(x, str) and x else None)

    yes_pattern = re.compile(r"^[\s|.|,]*(yes|true)[\s|.|,]*$", flags=re.IGNORECASE | re.MULTILINE)
    no_pattern = re.compile(r"^[\s|.|,]*(No|false)[\s|.|,]*$", flags=re.IGNORECASE | re.MULTILINE)

    logger.info(f"Converting to bools: {convert_to_boolean}")
    for col in convert_to_boolean:
        logger.debug(col)
        if col in split_by_pipe:
            data_table[col] = data_table[col].progress_apply(
                lambda x: (
                    [
                        (
                            True
                            if text and not isinstance(text, bool) and re.match(yes_pattern, text)
                            else (False if text and not isinstance(text, bool) and re.match(no_pattern, text) else text)
                        )
                        for text in x
                    ]
                    if x
                    else None
                )
            )

        else:
            data_table[col] = data_table[col].progress_apply(
                lambda text: (
                    True
                    if text and not isinstance(text, bool) and re.match(yes_pattern, text)
                    else (False if text and not isinstance(text, bool) and re.match(no_pattern, text) else text)
                )
            )
    norm_loc = NormalizeLocation(
        gadm_path="Database/data/gadm_world.csv",
        unsd_path="Database/data/UNSD — Methodology.csv",
    )

    logger.info("Extracting list of administrative areas and locations")
    data_table[["_Administrative_Area", "_Location"]] = (
        data_table["Location_raw"].progress_apply(norm_loc.extract_locations).progress_apply(pd.Series)
    )
    for i in ["_Administrative_Area", "_Location"]:
        data_table[i] = data_table[i].replace(float("nan"), None)

    logger.info("Normalizing administrative areas")
    data_table["Administrative_Area_Norm"] = data_table["_Administrative_Area"].progress_apply(
        lambda admin_areas: (
            [norm_loc.normalize_locations(area=c, is_country=True)[0] for c in admin_areas] if admin_areas else []
        )
    )
    
   # Second part: Get GIDs based on the normalized areas
    data_table["Administrative_Area_GID"] = data_table["Administrative_Area_Norm"].progress_apply(
        lambda areas: [
            norm_loc.get_gadm_gid(country=area)  # Call get_gadm_gid for each area in the list
            for area in areas  # Iterate through each area in the list of areas
            if area  # Ensure the area is not empty or None
        ] if isinstance(areas, list) else []  # Check if 'areas' is a list
    )



    logger.info("Normalizing locations")
    data_table["Location_Norm"] = data_table.progress_apply(
        lambda row: (
            [
                ([norm_loc.normalize_locations(area=a) if a else None for a in area_list] if area_list else None)
                for area_list in row["_Location"]
            ]
            if row["_Location"]
            else None
        ),
        axis=1,
    )
    data_table["Location_Norm"] = data_table["Location_Norm"].progress_apply(
        lambda location_list: (
            [[x[0] if x else None for x in area] if area else [] for area in location_list] if location_list else []
        )
    )
    data_table["Locations_GID"] = data_table["Location_Norm"].progress_apply(
    lambda location_list: [
        # Iterate through each nested list (each group of areas) and each area in that group
        (
            norm_loc.get_gadm_gid(country=area) or norm_loc.get_gadm_gid(area=area)
        )
        for sublist in location_list  # Iterate over each sublist (group of areas)
        for area in sublist          # Iterate over each area within the sublist
        if area                      # Only process non-empty areas
    ] if isinstance(location_list, list) else []
)


    logger.info("Splitting main events (l1) from specific instabnces (l3)")
    data_table["main"] = data_table.Event_ID_decimal.progress_apply(lambda x: float(x).is_integer())

    # data_table["Location_Norm"] = data_table["Location_raw"].progress_apply(lambda x: [])
    # Level 1 -- "Main Events"
    Events = data_table[data_table["main"] == True][[x for x in target_columns if x in data_table.columns]]
    Events["Administrative_Area_Norm"] = Events["Administrative_Area_Norm"].progress_apply(
        lambda x: list(set(x)) if x else None
    )

    Events.rename(columns={"Administrative_Area_Norm": "Administrative_Areas_Norm"}, inplace=True)
    Events.drop(columns=["Location_Norm"], inplace=True)

    total_columns_rename_keys = [
        x
        for x in Events.columns
        if any([x.endswith(y) for y in ["_Min", "_Max", "_Unit", "_Adjusted_Year", "_Adjusted"]])
        and not x.startswith("Total_")
    ]
    total_columns_rename_values = [f"Total_{x}" for x in total_columns_rename_keys]
    total_columns_map = {
        total_columns_rename_keys[i]: total_columns_rename_values[i] for i in range(len(total_columns_rename_keys))
    }
    logger.info(f"Renaming columns to 'Total_...`. Mapping: {total_columns_map}")

    Events.rename(columns=total_columns_map, inplace=True)
    

    # Level 3 -- "Specific Instances per country-level Administrative Area"
    # single administrative area with multiple sub locations
    Specific_Instance_Per_Administrative_Area = data_table[
        ~data_table["Administrative_Area_Norm"].progress_apply(lambda x: flatten(x) == [])
    ]
    Specific_Instance_Per_Administrative_Area = Specific_Instance_Per_Administrative_Area[
        Specific_Instance_Per_Administrative_Area["main"] == False
    ]

    event_breakdown_dfs = {}

    for name, df_lvl in {
        "Specific_Instance_Per_Administrative_Area": Specific_Instance_Per_Administrative_Area,  # l3
    }.items():
        for col_type in event_breakdown_columns.keys():
            logger.info(
                f"Processing {col_type}: {[event_breakdown_columns[col_type][x] for x in event_breakdown_columns[col_type].keys()]}"
            )
            event_breakdown_target_columns_base = shared_cols.copy()
            event_breakdown_target_columns_base.extend(location_cols)
            event_breakdown_target_columns_base.extend(date_cols)

            for cat in event_breakdown_columns[col_type]:
                event_breakdown_target_columns = event_breakdown_target_columns_base.copy()
                event_breakdown_target_columns.extend(event_breakdown_columns[col_type][cat])
                event_breakdown_dfs[f"{name}_{cat}_target_columns"] = event_breakdown_target_columns
                if not any([x in data_table.columns for x in event_breakdown_columns[col_type][cat]]):
                    break
                else:
                    logger.debug("Only store available columns")
                    availble_col = [x for x in event_breakdown_target_columns if x in data_table.columns]
                    logger.debug(
                        f"Desired columns: {event_breakdown_target_columns}.\nAvailable columns: {availble_col}"
                    )

                    df = df_lvl[flatten([availble_col, ["main"]])].copy()

                    logger.debug(f"Dropping rows missing specific impacts: {df.shape}")
                    missing_spec_impact_msk = df[event_breakdown_columns[col_type][cat]].isna().all(axis=1)
                    df = df[~missing_spec_impact_msk]

                    if name == "Specific_Instance_Per_Administrative_Area":  # l3
                        df["Administrative_Area_Norm"] = df["Administrative_Area_Norm"].progress_apply(
                            lambda x: (x if isinstance(x, list) else None)
                        )
                        df["Location_Norm"] = df["Location_Norm"].apply(lambda x: flatten(x) if x else [])
                        df = df[availble_col]
                        df.rename(
                            columns={"Location_Norm": "Locations_Norm"},
                            inplace=True,
                        )
                        event_breakdown_dfs[f"{name}_{cat}"] = df
                    del event_breakdown_target_columns, availble_col, df

    return Events, event_breakdown_dfs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    logger = Logging.get_logger("import gold data from excel", level="INFO")

    parser.add_argument(
        "-i",
        "--input-file",
        dest="input_file",
        help="The path to the excel file",
        default="Database/gold/ImpactDB_DataTable_Validation.xlsx",
        type=str,
    )

    parser.add_argument(
        "-s",
        "--sheet-name",
        dest="sheet_name",
        help="The name of the target sheet in the excel file",
        default="ImpactDB_v2_gold_template",
        type=str,
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        help="A dir to output main and specific impact events",
        default="Database/gold/impactdbv2",
        type=str,
    )

    parser.add_argument(
        "-n",
        "--no-rate-limiter",
        dest="no_rate_limiter",
        help="Pass to disable limiting API calls (to comply with Nominatim) with RateLimiter",
        action="store_true",
    )

    args = parser.parse_args()

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    Events, event_breakdown_dfs = flatten_data_table()

    logger.info("Storing Main Events table")
    lvl = "l1"
    if "split" in Events.columns:
        for i in Events["split"].unique():
            l1_output = f"{args.output_dir}/{i}/{lvl}"
            logger.info(f"Creating {l1_output} if it does not exist!")
            pathlib.Path(f"{l1_output}").mkdir(parents=True, exist_ok=True)

            Events[Events["split"] == i][[x for x in Events.columns if x != "split"]].to_parquet(
                f"{l1_output}/Total_Summary.parquet",
                engine="fastparquet",
            )
    else:
        pathlib.Path(f"{args.output_dir}/{lvl}").mkdir(parents=True, exist_ok=True)
        Events.to_parquet(
            f"{args.output_dir}/{lvl}/Total_Summary.parquet",
            engine="fastparquet",
        )
    for name, df in event_breakdown_dfs.items():
        if "_target_columns" not in name:
            logger.info(f"Fixing column names for {name}")
            df = fix_column_names(df)

            logger.info(f"Storing {name} table")
            if "split" in df.columns:
                for i in df["split"].unique():
                    lvl = "l3" if "Specific_" in name else "l2"
                    lvl_output = f"{args.output_dir}/{i}/{lvl}"
                    logger.info(f"Creating {lvl_output} if it does not exist!")
                    pathlib.Path(lvl_output).mkdir(parents=True, exist_ok=True)
                    df[df["split"] == i][[x for x in df.columns if x != "split"]].to_parquet(
                        f"{lvl_output}/{name}.parquet",
                        engine="fastparquet",
                    )
            else:
                df.to_parquet(
                    f"{args.output_dir}/{name}.parquet",
                    engine="fastparquet",
                )
