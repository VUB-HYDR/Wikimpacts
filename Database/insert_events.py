import argparse
import ast
import os
import pathlib
import sqlite3

import pandas as pd
from pandarallel import pandarallel
from tqdm import tqdm

from Database.scr.normalize_utils import (
    CategoricalValidation,
    GeoJsonUtils,
    Logging,
    NormalizeUtils,
)

pandarallel.initialize(progress_bar=False, nb_workers=5)

if __name__ == "__main__":
    event_levels = {
        "l1": {
            "prefix": "Total_Summary",
            "location_columns": {"Administrative_Areas": list},
        },
        "l2": {
            "prefix": "Instance_Per_Administrative_Areas_",
            "location_columns": {"Administrative_Areas": list},
        },
        "l3": {
            "prefix": "Specific_Instance_Per_Administrative_Area_",
            "location_columns": {
                "Administrative_Area": str,
                "Locations": list,
            },
        },
    }
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--method",
        dest="method",
        default="append",
        choices=["append", "replace"],
        help="Choose whether to append data to the exisitng db or to replace it",
        type=str,
    )

    parser.add_argument(
        "-f",
        "--file_dir",
        dest="file_dir",
        default="Database/output/dev",
        help="The directory where .parquet files exist so they can be inserted into the db",
        type=str,
    )

    parser.add_argument(
        "-db",
        "--database_name",
        dest="database_name",
        default="impact.v0.db",
        help="The name of your database (followed by the extension name, such as ´.db´)",
        type=str,
    )

    parser.add_argument(
        "-lvl",
        "--event_level",
        dest="event_level",
        required=True,
        help="The event level to parse. Pass only 1",
        choices=event_levels.keys(),
        type=str,
    )

    parser.add_argument(
        "-t",
        "--target_table",
        dest="target_table",
        default=None,
        required=False,
        help="Must be a table in the target database. Example: `Instance_Per_Administrative_Areas_Deaths`. For l2 and l3 only!",
        type=str,
    )

    parser.add_argument(
        "-gj",
        "--dump_geojson_to_file",
        dest="dump_geojson_to_file",
        action="store_true",
        help="Pass to replace geojson columns to filenames where the geojson object is stored.",
        required=False,
    )

    parser.add_argument(
        "-nid",
        "--nid_path",
        dest="nid_path",
        default="tmp/geojson_no_dupl",
        required=True,
        help="Where to store geojson with nid as filename.",
        type=str,
    )

    parser.add_argument(
        "-err",
        "--error_path",
        dest="error_path",
        default="tmp",
        required=False,
        help="Where to store insertion errors if found.",
        type=str,
    )

    args = parser.parse_args()
    logger = Logging.get_logger(f"database-insertion", level="INFO", filename="v1_full_run_insertion_raw.log")
    utils = NormalizeUtils()
    validation = CategoricalValidation()

    connection = sqlite3.connect(args.database_name)
    cursor = connection.cursor()
    files = os.listdir(args.file_dir)
    errors = pd.DataFrame()

    # levels
    main_level = "l1"
    sub_levels = [x for x in event_levels.keys() if x != "l1"]

    if args.dump_geojson_to_file:
        geojson_utils = GeoJsonUtils(nid_path=args.nid_path)
    if args.event_level == main_level:
        args.target_table = "Total_Summary"
        logger.info(f"Inserting {main_level}...\n")
        for f in tqdm(files, desc="Files"):
            data = pd.read_parquet(f"{args.file_dir}/{f}", engine="fastparquet")
            data = utils.replace_nulls(data)

            # turn invalid currencies to None (for L1 only)
            data = data.parallel_apply(lambda row: validation.validate_currency_monetary_impact(row), axis=1)

            # geojson in l1 is always of type list
            if args.dump_geojson_to_file:
                for col in event_levels[args.event_level]["location_columns"].keys():
                    logger.info(f"Processing GeoJson column {col}_GeoJson in {args.event_level}; File: {f}")

                    for i in ["GeoJson", "Norm"]:
                        data[f"{col}_{i}"] = data[f"{col}_{i}"].parallel_apply(
                            lambda x: ast.literal_eval(x) if isinstance(x, str) else []
                        )

                    data[f"{col}_GeoJson"] = data.parallel_apply(
                        lambda row: (
                            [
                                geojson_utils.geojson_to_file(row[f"{col}_GeoJson"][i], row[f"{col}_Norm"][i])
                                for i in range(len(row[f"{col}_Norm"]))
                            ]
                            if isinstance(row[f"{col}_GeoJson"], list)
                            and len(row[f"{col}_GeoJson"]) == len(row[f"{col}_Norm"])
                            else []
                        ),
                        axis=1,
                    )

            logger.info("Converting everything to strings...")
            data.replace(float("nan"), None, inplace=True)
            for c in data.columns:
                data[c] = data[c].astype(str)

            # change if_exists to "append" to avoid overwriting the database
            # choose "replace" to overwrite the database with a fresh copy of the data
            for i in tqdm(range(len(data)), desc=f"Inserting {args.event_level} into {args.database_name}"):
                try:
                    data.iloc[i : i + 1].to_sql(
                        name=args.target_table,
                        con=connection,
                        if_exists=args.method,
                        index=False,
                    )
                except sqlite3.IntegrityError as err:
                    logger.debug(
                        f"""Could not insert event for level {args.event_level}. Error {err}.
                                The problematic row will be stored in /tmp/ with the error. GeoJson columns will not be included."""
                    )
                    err_row = data.iloc[i : i + 1][[x for x in data.columns if "GeoJson" not in x]].copy()
                    err_row["ERROR"] = err
                    errors = pd.concat([errors, err_row], ignore_index=True)

    elif args.event_level in sub_levels:
        logger.info(f"Inserting {args.event_level}...\n")
        assert args.target_table, f"When inserting sublevels ({sub_levels}), the target table must be specified!"

        check_table = cursor.execute(
            f"""SELECT name FROM sqlite_master WHERE type='table'
                AND name='{args.target_table}'; """
        ).fetchall()

        assert len(check_table) == 1, f"Table name {args.target_table} incorrect! Found {check_table} instead."

        for f in tqdm(files, desc="Files"):
            data = pd.read_parquet(f"{args.file_dir}/{f}", engine="fastparquet")
            data = utils.replace_nulls(data)

            logger.info(f"Popping GeoJson files out for level {args.event_level} and onto disk")
            if args.dump_geojson_to_file:
                for col, _type in event_levels[args.event_level]["location_columns"].items():
                    logger.info(f"Processing GeoJson column {col} in {args.event_level}; File: {f}")
                    if _type == list:
                        data[f"{col}_GeoJson"] = data.parallel_apply(
                            lambda row: (
                                [
                                    geojson_utils.geojson_to_file(row[f"{col}_GeoJson"][i], row[f"{col}_Norm"][i])
                                    for i in range(len(row[f"{col}_Norm"]))
                                ]
                                if isinstance(row[f"{col}_GeoJson"], list)
                                and len(row[f"{col}_GeoJson"]) == len(row[f"{col}_Norm"])
                                else []
                            ),
                            axis=1,
                        )

                    elif _type == str:
                        data[f"{col}_GeoJson"] = data.parallel_apply(
                            lambda row: (
                                geojson_utils.geojson_to_file(row[f"{col}_GeoJson"], row[f"{col}_Norm"])
                                if isinstance(row[f"{col}_GeoJson"], str)
                                else None
                            ),
                            axis=1,
                        )

            # change if_exists to "append" to avoid overwriting the database
            # choose "replace" to overwrite the database with a fresh copy of the data
            logger.info("Converting everything to strings...")
            data.replace(float("nan"), None, inplace=True)
            for c in data.columns:
                data[c] = data[c].astype(str)

            for i in tqdm(range(len(data)), desc=f"Inserting {args.event_level} into {args.database_name}"):
                try:
                    data.iloc[i : i + 1].to_sql(
                        name=args.target_table,
                        con=connection,
                        if_exists=args.method,
                        index=False,
                    )
                except sqlite3.IntegrityError as err:
                    logger.debug(
                        f"""Could not insert event for level {args.event_level}. Error {err}.
                                The problematic row will be stored in tmp/ with the error. GeoJson columns will not be included."""
                    )
                    err_row = data.iloc[i : i + 1][[x for x in data.columns if "GeoJson" not in x]].copy()
                    err_row["ERROR"] = err
                    errors = pd.concat([errors, err_row], ignore_index=True)

    geojson_utils.store_non_english_nids()

    if errors.shape != (0, 0):
        from time import time

        tmp_errors_filename = (
            f"{args.error_path}/db_insert_errors_{args.event_level}_{args.target_table}_{int(time())}.json"
        )
        logger.error(f"Insert errors were found! THIS ROW WAS NOT INSERTED! Storing in {tmp_errors_filename}")
        pathlib.Path(args.error_path).mkdir(parents=True, exist_ok=True)
        errors.to_json(tmp_errors_filename, orient="records", indent=3)
    connection.close()
