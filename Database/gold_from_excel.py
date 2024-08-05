import argparse
import pathlib
import re

import pandas as pd

# delete Database.
from scr.normalize_utils import Logging

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


# prepare columns
# if new columns become part of the schema, edit them to this file
def flatten(xss):
    return [x for xs in xss for x in xs]


# set specific impact columns
specific_impacts_columns = {
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
        "Homelessness_Min",
        "Homelessness_Max",
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

# main and specific impact events have these three column sets in common
shared_cols = [
    "Event_ID",
    "Event_ID_decimal",
    "Source",
    "Event_Name",
]

location_cols = ["Location", "Country_Norm (Last update: 15th of May, 2024)"]

date_cols = [
    "Start_Date_Month",
    "Start_Date_Day",
    "End_Date_Year",
    "End_Date_Month",
    "End_Date_Day",
]

# set main events output target columns
target_columns = flatten(
    [shared_cols, location_cols, date_cols, flatten([x for x in specific_impacts_columns.values()])]
)

# get min,max range columns
range_only_col = []
for i in specific_impacts_columns.keys():
    if len(specific_impacts_columns[i]) == 2:
        range_only_col.extend(specific_impacts_columns[i])

# get string type columns
convert_to_str = flatten([shared_cols, location_cols])
for i in ["Insured_Damage", "Damage"]:
    convert_to_str.extend([x for x in specific_impacts_columns[i] if "_Min" not in x or "_Max" not in x])

# get int type columns
convert_to_int = flatten([date_cols, range_only_col])

# get "list" type columns with a list of integers
convert_to_int_list = []
for i in ["Insured_Damage", "Damage"]:
    convert_to_int_list.extend([x for x in specific_impacts_columns[i] if "_Min" in x or "_Max" in x or "_Year" in x])

# get "list" type columns with pipe separator
split_by_pipe = flatten(
    [
        ["Event_Name", "Source", "Hazard"],
        specific_impacts_columns["Insured_Damage"],
        specific_impacts_columns["Damage"],
    ]
)

# get bool type columns
convert_to_boolean = []
for i in ["Insured_Damage", "Damage"]:
    convert_to_boolean.extend([x for x in specific_impacts_columns[i] if "_Adjusted" in x and "_Year" not in x])

convert_to_float = ["Event_ID_decimal"]


# change the excel input to csv format
def flatten_data_table():
    logger.info("Loading csv file...")
    data_table = pd.read_csv(args.input_file, encoding="ISO-8859-1", na_filter=False)
    logger.info(f"Shape: {data_table.shape}")

    logger.info("Dropping blank cells...")
    data_table.dropna(
        how="all",
        inplace=True,
    )
    logger.info(f"Shape: {data_table.shape}")

    logger.info("Fixing column names...")
    data_table = data_table[target_columns]

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

    logger.info(f"Converting list values to ints in {convert_to_int_list}")
    for col in convert_to_int_list:
        logger.debug(col)
        data_table[col] = data_table[col].apply(
            lambda x: (None if x is None else [int(y.strip()) for y in x if str(y).isdigit()])
        )

    yes_pattern = re.compile(r"^[\s|.|,]*(yes|true)[\s|.|,]*$", flags=re.IGNORECASE | re.MULTILINE)
    no_pattern = re.compile(r"^[\s|.|,]*(No|false)[\s|.|,]*$", flags=re.IGNORECASE | re.MULTILINE)

    for col in convert_to_boolean:
        logger.debug(col)
        data_table[col] = data_table[col].apply(
            lambda bool_list: (
                [False if not isinstance(x, bool) and re.match(no_pattern, x) else x for x in bool_list]
                if bool_list
                else None
            )
        )
        data_table[col] = data_table[col].apply(
            lambda bool_list: (
                [True if not isinstance(x, bool) and re.match(yes_pattern, x) else x for x in bool_list]
                if bool_list
                else None
            )
        )

    logger.info("Splitting main events from specific impact")
    data_table["main"] = data_table.Event_ID_decimal.apply(lambda x: float(x).is_integer())
    data_table["main"].value_counts()

    logger.info("Storing Main Events table")
    Events = data_table[data_table["main"] == True][target_columns]
    # change the column name of main gold data for evaluation
    # Map the old columns to the new columns with default values
    new_columns_mapping_gold = {
        "Total_Deaths_Min": "Deaths_Min",
        "Total_Deaths_Max": "Deaths_Max",
        "Total_Injuries_Max": "Injured_Max",
        "Total_Injuries_Min": "Injured_Min",
        "Total_Displace_Min": "Displaced_Min",
        "Total_Displace_Max": "Displaced_Max",
        "Total_Affected_Min": "Affected_Min",
        "Total_Affected_Max": "Affected_Max",
        "Total_Homeless_Min": "Homelessness_Min",
        "Total_Homeless_Max": "Homelessness_Max",
        "Total_Buildings_Min": "Buildings_Damaged_Min",
        "Total_Buildings_Max": "Buildings_Damaged_Max",
        "Total_Damage_Min": "Damage_Min",
        "Total_Damage_Max": "Damage_Max",
        "Total_Damage_Units": "Damage_Units",
        "Total_Damage_Inflation_Adjusted": "Damage_Inflation_Adjusted",
        "Total_Damage_Inflation_Adjusted_Year": "Damage_Inflation_Adjusted_Year",
        "Country_Norm": "Country_Norm (Last update: 15th of May, 2024)",
        "Total_Insured_Damage_Min": "Insured_Damage_Min",
        "Total_Insured_Damage_Max": "Insured_Damage_Max",
        "Total_Insured_Damage_Units": "Insured_Damage_Unit",
        "Total_Insured_Damage_Inflation_Adjusted": "Insured_Damage_Inflation_Adjusted",
        "Total_Insured_Damage_Inflation_Adjusted_Year": "Insured_Damage_Inflation_Adjusted_Year",
    }
    for new_col, old_col in new_columns_mapping_gold.items():
        Events[new_col] = Events[old_col]
    Events.to_parquet(
        f"{args.output_dir}/Events.parquet",
        engine="fastparquet",
    )

    specific_impacts_dfs = {}
    for spec in specific_impacts_columns.keys():
        logger.info(f"Processing {spec}")
        spec_target_columns = shared_cols.copy()
        spec_target_columns.extend(location_cols)
        spec_target_columns.extend(date_cols)
        spec_target_columns.extend(specific_impacts_columns[spec])
        specific_impacts_dfs[f"{spec}_target_columns"] = spec_target_columns

        logger.info(f"Target columns: {spec_target_columns}")
        df = data_table[flatten([spec_target_columns, ["main"]])].copy()

        missing_date_msk = df[date_cols].isna().all(axis=1)
        missing_spec_impact_msk = df[date_cols].isna().all(axis=1)
        logger.debug(f"Dropping rows missing dates: {df.shape}")

        df = df[~missing_date_msk]

        logger.debug(f"Dropping rows missing specific impacts: {df.shape}")
        df = df[~missing_spec_impact_msk]

        specific_impacts_dfs[spec] = df[df["main"] == False][spec_target_columns]
        del spec_target_columns
        del df

    for name, df in specific_impacts_dfs.items():
        if "_target_columns" not in name:
            logger.info(f"Storing {name} table")
            df.to_parquet(f"{args.output_dir}/{name}.parquet", engine="fastparquet")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    logger = Logging.get_logger("import gold data from excel")

    parser.add_argument(
        "-i",
        "--input-file",
        dest="input_file",
        help="The path to the csv file",
        type=str,
    )
    """
    parser.add_argument(
        "-s",
        "--sheet-name",
        dest="sheet_name",
        help="The name of the target sheet in the excel file",
        type=str,
    )
    """

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

    flatten_data_table()
