import argparse
import pathlib
import re

import pandas as pd

from Database.scr.normalize_locations import NormalizeLocation
from Database.scr.normalize_utils import Logging

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


def flatten(xss):
    return [x for xs in xss for x in xs]


def fix_column_names(df):
    mapper = {
        "_Min": "Num_Min",
        "_Max": "Num_Max",
        "_Unit": "Num_Unit",
        "_Units": "Num_Unit",
        "_Adjusted": "Num_Inflation_Adjusted",
        "_Adjusted_Year": "Num_Adjusted_Year",
    }

    for k, v in mapper.items():
        for col in df.columns:
            if col.endswith(k):
                df.rename(columns={col: v}, inplace=True)
    return df


# set specific impact columns
event_breakdown_columns = {
    "Injured": [
        "Injured_Min",
        "Injured_Max",
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
        "Damage_Units",
        "Damage_Inflation_Adjusted",
        "Damage_Inflation_Adjusted_Year",
    ],
}

# main events, impact per country events, and specific instance events have these three column sets in common
shared_cols = [
    "Event_ID",
    "Event_ID_decimal",
    "Sources",
    "Event_Names",
    "Hazards",
]

# TODO: add plural 's' for L1-2 for admin_area and for L3 for location
location_cols = ["Administrative_Area_Norm", "Location_Norm"]

date_cols = [
    "Start_Date_Year",
    "Start_Date_Month",
    "Start_Date_Day",
    "End_Date_Year",
    "End_Date_Month",
    "End_Date_Day",
]

# set main events output target columns
target_columns = flatten(
    [
        shared_cols,
        location_cols,
        date_cols,
        flatten([x for x in event_breakdown_columns.values()]),
    ]
)

# get min,max range columns
range_only_col = []
for i in event_breakdown_columns.keys():
    if len(event_breakdown_columns[i]) == 2:
        range_only_col.extend(event_breakdown_columns[i])

# get string type columns
convert_to_str = flatten([shared_cols])
for i in ["Insured_Damage", "Damage"]:
    convert_to_str.extend([x for x in event_breakdown_columns[i] if "_Min" not in x or "_Max" not in x])

# get int type columns
convert_to_int = flatten([date_cols, range_only_col])

# get "list" type columns with pipe separator
split_by_pipe = ["Event_Names", "Sources", "Hazards"]

# get bool type columns
convert_to_boolean = []
for i in ["Insured_Damage", "Damage"]:
    convert_to_boolean.extend([x for x in event_breakdown_columns[i] if "_Adjusted" in x and "_Year" not in x])

convert_to_float = ["Event_ID_decimal"]


def flatten_data_table():
    logger.info("Loading excel file...")
    data_table = pd.read_excel(args.input_file, sheet_name=args.sheet_name, engine="openpyxl", na_filter=False)
    logger.info(f"Shape: {data_table.shape}")

    logger.info("Dropping blank cells...")
    data_table.dropna(
        how="all",
        inplace=True,
    )
    # data_table = data_table[target_columns]
    logger.info(f"Shape: {data_table.shape}")

    logger.info("Normalizing all NULLs")  # to python NoneType...")
    for col in data_table.columns:
        pattern = re.compile(r"^[\s|.|,]*(null|nul)[\s|.|,]*$", flags=re.IGNORECASE | re.MULTILINE)
        data_table[col] = data_table[col].astype(str)
        data_table[col] = data_table[col].replace(pattern, None, regex=True)

    logger.info("Fixing data types")

    logger.info(f"Converting to integers: {convert_to_int}")
    for col in convert_to_int:
        logger.debug(col)
        data_table[col] = data_table[col].apply(
            lambda x: (None if x is None else (int(x.strip()) if str(x).isdigit() else None))
        )
    logger.info("Dropping bad dates...")
    for col in date_cols:
        data_table[col] = data_table[col].replace(0.0, None)

    data_table.dropna(how="all", inplace=True, subset=date_cols)

    logger.info(f"Converting to strings: {convert_to_str}")
    for col in convert_to_str:
        logger.debug(col)
        data_table[col] = data_table[col].apply(lambda x: None if x is None else str(x).strip())

    logger.info(f"Splitting by pipes: {split_by_pipe}")
    for col in split_by_pipe:
        logger.debug(col)
        data_table[col] = data_table[col].apply(
            lambda x: [y.strip() for y in x.split("|")] if isinstance(x, str) else None
        )

    logger.info(f"Converting to floats: {convert_to_float}")
    for col in convert_to_float:
        logger.debug(col)
        data_table[col] = data_table[col].apply(lambda x: float(x) if isinstance(x, str) else None)

    yes_pattern = re.compile(r"^[\s|.|,]*(yes|true)[\s|.|,]*$", flags=re.IGNORECASE | re.MULTILINE)
    no_pattern = re.compile(r"^[\s|.|,]*(No|false)[\s|.|,]*$", flags=re.IGNORECASE | re.MULTILINE)

    logger.info(f"Converting to bools: {convert_to_boolean}")
    for col in convert_to_boolean:
        logger.debug(col)
        data_table[col] = data_table[col].apply(
            lambda text: (True if text and not isinstance(text, bool) and re.match(yes_pattern, text) else text)
        )
        data_table[col] = data_table[col].apply(
            lambda text: (False if text and not isinstance(text, bool) and re.match(no_pattern, text) else text)
        )

    norm_loc = NormalizeLocation(
        gadm_path="Database/data/gadm_world.csv",
        unsd_path="Database/data/UNSD — Methodology.csv",
    )

    logger.info("Extracting list of administrative areas and locations")
    data_table[["_Administrative_Area", "_Location"]] = (
        data_table["Location"].apply(norm_loc.extract_locations).apply(pd.Series)
    )

    logger.info("Extracting list of administrative areas and locations")
    data_table[["_Administrative_Area", "_Location"]] = (
        data_table["Location"].apply(norm_loc.extract_locations).apply(pd.Series)
    )

    logger.info("Normalizing administrative areas")
    data_table["Administrative_Area_Norm"] = data_table["_Administrative_Area"].apply(
        lambda admin_areas: [norm_loc.normalize_locations(area=c, is_country=True)[0] for c in admin_areas]
        if admin_areas
        else []
    )

    logger.info("Normalizing locations")
    data_table["Location_Norm"] = data_table.apply(
        lambda row: [
            [norm_loc.normalize_locations(area=a) if a else None for a in area_list] if area_list else None
            for area_list in row["_Location"]
        ],
        axis=1,
    )
    data_table["Location_Norm"] = data_table["Location_Norm"].apply(
        lambda location_list: [[x[0] if x else None for x in area] if area else [] for area in location_list]
        if location_list
        else []
    )
    logger.info("Splitting main events from specific impact")
    data_table["main"] = data_table.Event_ID_decimal.apply(lambda x: float(x).is_integer())

    # Level 1 -- "Main Events"
    Events = data_table[data_table["main"] == True][target_columns]

    # Level 3 -- "Impacts Per country-level Administrative Area"
    Impacts = data_table[data_table["Location_Norm"].apply(lambda x: flatten(x) == [])]

    # Level 2 -- "Specific Instances per country-level Administrative Area"
    Specific_Instances = data_table[~data_table["Location_Norm"].apply(lambda x: flatten(x) == [])]

    event_breakdown_dfs = {}
    for name, df_lvl in {"Impacts": Impacts, "Specific_Instances": Specific_Instances}.items():
        for e in event_breakdown_columns.keys():
            logger.info(f"Processing {e}")
            event_breakdown_target_columns = shared_cols.copy()
            event_breakdown_target_columns.extend(location_cols)
            event_breakdown_target_columns.extend(date_cols)
            event_breakdown_target_columns.extend(event_breakdown_columns[e])
            event_breakdown_dfs[f"{name}_{e}_target_columns"] = event_breakdown_target_columns

            logger.info(f"Target columns: {event_breakdown_target_columns}")
            df = df_lvl[flatten([event_breakdown_target_columns, ["main"]])].copy()

            missing_date_msk = df[date_cols].isna().all(axis=1)
            missing_spec_impact_msk = df[event_breakdown_columns[e]].isna().all(axis=1)
            logger.debug(f"Dropping rows missing dates: {df.shape}")
            df = df[~missing_date_msk]

            logger.debug(f"Dropping rows missing specific impacts: {df.shape}")
            df = df[~missing_spec_impact_msk]

            if name == "Impacts":
                df.Administrative_Area_Norm = df.Administrative_Area_Norm.apply(lambda x: x[0])
                event_breakdown_dfs[f"{e}_Per_Country"] = df[df["main"] == False][
                    [x for x in event_breakdown_target_columns if x != "Location_Norm"]
                ]
            else:
                event_breakdown_dfs[f"{name}_{e}_Per_Country"] = df[df["main"] == False][event_breakdown_target_columns]
            del event_breakdown_target_columns
            del df
    return Events, event_breakdown_dfs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    logger = Logging.get_logger("import gold data from excel")

    parser.add_argument(
        "-i",
        "--input-file",
        dest="input_file",
        help="The path to the excel file",
        type=str,
    )

    parser.add_argument(
        "-s",
        "--sheet-name",
        dest="sheet_name",
        help="The name of the target sheet in the excel file",
        type=str,
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        help="A dir to output main and specific impact events",
        type=str,
    )

    args = parser.parse_args()

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    Events, event_breakdown_dfs = flatten_data_table()

    logger.info("Storing Main Events table")
    Events.to_parquet(
        f"{args.output_dir}/Events.parquet",
        engine="fastparquet",
    )

    for name, df in event_breakdown_dfs.items():
        if "_target_columns" not in name:
            logger.info(f"Storing {name} table")
            logger.info(f"Fixing column names for {name}")

            df = fix_column_names(df)
            df.to_parquet(f"{args.output_dir}/{name}.parquet", engine="fastparquet")
