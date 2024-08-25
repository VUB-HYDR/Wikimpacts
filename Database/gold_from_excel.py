import argparse
import pathlib
import re
from datetime import datetime

import pandas as pd
from iso4217 import Currency

from Database.scr.normalize_utils import Logging

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


def flatten(xss):
    return [x for xs in xss for x in xs]


def fix_column_names(df):
    # TODO: L2 and L3 differ here!
    mapper = {
        "_Min": "Num_Min",
        "_Max": "Num_Max",
        "_Units": "Num_Units",
        "_Adjusted": "Num_Inflation_Adjusted",
        "_Adjusted_Year": "Num_Adjusted_Year",
    }

    for k, v in mapper.items():
        for col in df.columns:
            if col.endswith(k):
                df.rename(columns={col: v}, inplace=True)
    return df


def _check_currency(currency_text: str) -> bool:
    try:
        Currency(currency_text)
        return True
    except ValueError:
        return False


def _check_date(year: int, month: int, day: int) -> bool:
    try:
        datetime(year, month, day)
        return True
    except ValueError:
        return False


def _split_range(text: str) -> tuple[float, None]:
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

# L1, L2, and L3 have these three column sets in common
shared_cols = [
    "Event_ID",
    "Event_ID_decimal",
    "Sources",
    "Event_Names",
    "Hazards",
    "split",  # dataset split; example: dev/test
]

location_cols = []  # ["Administrative_Area_Norm", "Location_Norm"]

date_cols = [
    "Start_Date_Year",
    "Start_Date_Month",
    "Start_Date_Day",
    "End_Date_Year",
    "End_Date_Month",
    "End_Date_Day",
]

# set L1 output target columns
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

# get numeric type columns
numeric_type_col = []
for i in event_breakdown_columns["numerical"].keys():
    numeric_type_col.extend(event_breakdown_columns["numerical"][i])

# get string type columns
convert_to_str = flatten([shared_cols])
convert_to_int = flatten([date_cols, numeric_type_col])
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

    logger.info("Dropping bad dates or rows with missing dates...")
    # TODO: this may be a step we want to skip with gold data imports
    # TODO: does this remove l2/l3 that are 'automatically filled' but missing dates?
    for col in date_cols:
        data_table[col] = data_table[col].replace(0.0, None)
        data_table = data_table.replace(float("nan"), None)
    data_table.dropna(how="all", inplace=True, subset=date_cols)

    logger.info(f"Converting to integers: {convert_to_int}")
    for col in convert_to_int:
        logger.debug(f"Casting column {col} as int")
        if col in data_table.columns:
            data_table[col] = data_table[col].apply(
                lambda x: (None if x is None else (int(x.strip()) if str(x).isdigit() else None))
            )
    data_table = data_table.replace(float("nan"), None)

    logger.info(f"Converting to strings: {convert_to_str}")
    for col in convert_to_str:
        logger.debug(col)
        data_table[col] = data_table[col].apply(lambda x: None if x is None else str(x).strip())

    logger.info(f"Splitting by pipes: {split_by_pipe} and normalizing NULLs in the output lists")
    for col in split_by_pipe:
        logger.debug(f"Casting column {col} as list")
        data_table[col] = data_table[col].apply(lambda x: [y for y in x.split("|")] if isinstance(x, str) else None)
        data_table[col] = data_table[col].apply(
            lambda x: ([None if re.match(null_pattern, text) else text for text in x] if x else None)
        )
    logger.info(f"Validating Units for monetary type columns...")
    for col in currency_unit_cols:
        data_table[f"{col}_valid_currency"] = data_table[col].apply(
            lambda x: all([_check_currency(y) for y in x]) if x else True
        )
        assert all(data_table[f"{col}_valid_currency"])
        data_table.drop(columns=[f"{col}_valid_currency"], inplace=True)

    logger.info(f"Validating Dates...")

    for col in date_cols:
        if col.endswith("Year"):
            data_table[f"{col}_valid_year"] = data_table[col].apply(
                lambda x: (len(str(x).split(".")[0]) == 4 and x > 0 and x <= datetime.now().year if x else True)
            )
            assert all(data_table[f"{col}_valid_year"])
            data_table.drop(columns=[f"{col}_valid_year"], inplace=True)

        if col.endswith("Month"):
            data_table[f"{col}_valid_month"] = data_table[col].apply(lambda x: x <= 12 and x > 0 if x else True)
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
        ].apply(lambda x: _check_date(x[0], x[1], x[2]) if all(x) else True)

        assert all(data_table[f"{date_type}_valid_date"])
        data_table.drop(columns=[f"{date_type}_valid_date"], inplace=True)

    # ranges need to be extracted from monetary column types, but not from the numerical column types
    for col_type in event_breakdown_columns["monetary"]:
        logger.info(f"Extracting ranges from {col_type} columns")
        for col in event_breakdown_columns["monetary"].keys():
            logger.info(f"Normalizing ranges for {col}")
            data_table[f"{col}_Min"] = data_table[col].apply(
                lambda x: [_split_range(y)[0] for y in x] if isinstance(x, list) else None
            )
            data_table[f"{col}_Max"] = data_table[col].apply(
                lambda x: [_split_range(y)[1] for y in x] if isinstance(x, list) else None
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
        if col in split_by_pipe:
            data_table[col] = data_table[col].apply(
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
            data_table[col] = data_table[col].apply(
                lambda text: (
                    True
                    if text and not isinstance(text, bool) and re.match(yes_pattern, text)
                    else (False if text and not isinstance(text, bool) and re.match(no_pattern, text) else text)
                )
            )
    """
    norm_loc = NormalizeLocation(
        gadm_path="Database/data/gadm_world.csv",
        unsd_path="Database/data/UNSD — Methodology.csv",
    )

    logger.info("Extracting list of administrative areas and locations")
    data_table[["_Administrative_Area", "_Location"]] = (
        data_table["Location_raw"].apply(norm_loc.extract_locations).apply(pd.Series)
    )

    logger.info("Extracting list of administrative areas and locations")
    data_table[["_Administrative_Area", "_Location"]] = (
        data_table["Location_raw"].apply(norm_loc.extract_locations).apply(pd.Series)
    )

    logger.info("Normalizing administrative areas")
    data_table["Administrative_Area_Norm"] = data_table["_Administrative_Area"].apply(
        lambda admin_areas: (
            [
                norm_loc.normalize_locations(area=c, is_country=True)[0]
                for c in admin_areas
            ]
            if admin_areas
            else []
        )
    )

    logger.info("Normalizing locations")
    data_table["Location_Norm"] = data_table.apply(
        lambda row: [
            (
                [norm_loc.normalize_locations(area=a) if a else None for a in area_list]
                if area_list
                else None
            )
            for area_list in row["_Location"]
        ],
        axis=1,
    )
    data_table["Location_Norm"] = data_table["Location_Norm"].apply(
        lambda location_list: (
            [
                [x[0] if x else None for x in area] if area else []
                for area in location_list
            ]
            if location_list
            else []
        )
    )
    """
    logger.info("Splitting main events from specific impact")
    data_table["main"] = data_table.Event_ID_decimal.apply(lambda x: float(x).is_integer())

    data_table["Location_Norm"] = data_table["Location_raw"].apply(lambda x: [])
    # Level 1 -- "Main Events"
    Events = data_table[data_table["main"] == True][[x for x in target_columns if x in data_table.columns]]

    # Level 3 -- "Impacts Per country-level Administrative Area"
    Impact_Per_Country = data_table[data_table["Location_Norm"].apply(lambda x: flatten(x) == [])]

    # Level 2 -- "Specific Instances per country-level Administrative Area"
    Specific_Instance_Per_Country = data_table[~data_table["Location_Norm"].apply(lambda x: flatten(x) == [])]

    event_breakdown_dfs = {}

    for name, df_lvl in {
        "Impact_Per_Country": Impact_Per_Country,  # l2
        "Specific_Instance_Per_Country": Specific_Instance_Per_Country,  # l3
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

                    event_breakdown_target_columns = availble_col
                    df = df_lvl[flatten([event_breakdown_target_columns, ["main"]])].copy()

                    logger.debug(f"Dropping rows missing dates: {df.shape}")
                    missing_date_msk = df[date_cols].isna().all(axis=1)
                    df = df[~missing_date_msk]

                    logger.debug(f"Dropping rows missing specific impacts: {df.shape}")
                    missing_spec_impact_msk = df[event_breakdown_columns[col_type][cat]].isna().all(axis=1)
                    df = df[~missing_spec_impact_msk]
                    if name == "Impact_Per_Country":
                        """
                        df.Administrative_Area_Norm = df.Administrative_Area_Norm.apply(
                            lambda x: x.split("|") if x else None #???#
                        )
                        """
                        event_breakdown_dfs[f"{cat}_{name}"] = df[df["main"] == False][
                            [x for x in event_breakdown_target_columns if x != "Location_Norm"]
                        ]
                    else:
                        event_breakdown_dfs[f"{cat}_{name}"] = df[df["main"] == False][event_breakdown_target_columns]
                    del event_breakdown_target_columns
                    del df

    return Events, event_breakdown_dfs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    logger = Logging.get_logger("import gold data from excel", level="DEBUG")

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

    args = parser.parse_args()

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    Events, event_breakdown_dfs = flatten_data_table()

    logger.info("Storing Main Events table")
    if "split" in Events.columns:
        for i in Events["split"].unique():
            logger.info(f"Creating {args.output_dir}/{i} if it does not exist!")
            pathlib.Path(f"{args.output_dir}/{i}").mkdir(parents=True, exist_ok=True)

            Events[Events["split"] == i][[x for x in Events.columns if x != "split"]].to_parquet(
                f"{args.output_dir}/{i}/Events.parquet",
                engine="fastparquet",
            )
    else:
        Events.to_parquet(
            f"{args.output_dir}/Events.parquet",
            engine="fastparquet",
        )

    for name, df in event_breakdown_dfs.items():
        if "_target_columns" not in name:
            logger.info(f"Storing {name} table")
            logger.info(f"Fixing column names for {name}")

            df = fix_column_names(df)
            if "split" in df.columns:
                for i in df["split"].unique():
                    logger.info(f"Creating {args.output_dir}/{i} if it does not exist!")
                    pathlib.Path(f"{args.output_dir}/{i}").mkdir(parents=True, exist_ok=True)

                    df[df["split"] == i][[x for x in df.columns if x != "split"]].to_parquet(
                        f"{args.output_dir}/{i}/{name}.parquet",
                        engine="fastparquet",
                    )
            else:
                df.to_parquet(
                    f"{args.output_dir}/{name}.parquet",
                    engine="fastparquet",
                )
