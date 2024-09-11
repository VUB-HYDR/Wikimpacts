import argparse
import ast
import os
import pathlib
import sqlite3

import pandas as pd
from tqdm import tqdm

tqdm.pandas()
from Database.scr.normalize_utils import GeoJsonUtils, Logging

if __name__ == "__main__":
    event_levels = {
        "l1": {
            "prefix": "Total_Summary",
            "location_columns": {"Administrative_Areas_GeoJson": list},
        },
        "l2": {
            "prefix": "Instance_Per_Administrative_Areas_",
            "location_columns": {"Administrative_Areas_GeoJson": list},
        },
        "l3": {
            "prefix": "Specific_Instance_Per_Administrative_Area_",
            "location_columns": {
                "Administrative_Area_GeoJson": str,
                "Locations_GeoJson": list,
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

    args = parser.parse_args()
    logger = Logging.get_logger(f"database-insertion", level="INFO")

    connection = sqlite3.connect(args.database_name)
    cursor = connection.cursor()
    files = os.listdir(args.file_dir)
    errors = pd.DataFrame()

    # levels
    main_level = "l1"
    sub_levels = [x for x in event_levels.keys() if x != "l1"]

    if args.event_level == main_level:
        args.target_table = "Total_Summary"
        logger.info(f"Inserting {main_level}...\n")
        for f in files:
            data = pd.read_parquet(f"{args.file_dir}/{f}", engine="fastparquet")
            # geojson in l1 is always of type list
            if args.dump_geojson_to_file:
                geojson_utils = GeoJsonUtils()
                logger.info(f"Popping GeoJson files out of {args.database_name} and onto disk")
                for col in event_levels[args.event_level]["location_columns"].keys():
                    logger.info(f"Processing GeoJson column {col} in {args.event_level}")
                    data[col] = data[col].progress_apply(
                        lambda x: (
                            [
                                geojson_utils.geojson_to_file(gj, output_dir=f"tmp/geojson/{args.event_level}")
                                for gj in ast.literal_eval(x)
                            ]
                            if isinstance(x, str)
                            else None
                        )
                    )
                    data[col] = data[col].astype(str)

            # change if_exists to "append" to avoid overwriting the database
            # choose "replace" to overwrite the database with a fresh copy of the data
        for i in tqdm(range(len(data))):
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

        for f in files:
            data = pd.read_parquet(f"{args.file_dir}/{f}", engine="fastparquet")

            # geojson in l2 and l3 may be a string or list!
            logger.info(f"Popping GeoJson files out of {args.database_name} and onto disk")
            geojson_utils = GeoJsonUtils()
            if args.dump_geojson_to_file:
                for col, _type in event_levels[args.event_level]["location_columns"].items():
                    logger.info(f"Processing GeoJson column {col} in {args.event_level}; File: {f}")
                    print()
                    print(data.columns)
                    print(f)
                    print()
                    if _type == list:
                        data[col] = data[col].progress_apply(
                            lambda x: (
                                [
                                    geojson_utils.geojson_to_file(gj, output_dir=f"tmp/geojson/{args.event_level}")
                                    for gj in ast.literal_eval(x)
                                ]
                                if isinstance(x, str)
                                else None
                            )
                        )
                        data[col] = data[col].astype(str)
                    elif _type == str:
                        data[col] = data[col].progress_apply(
                            lambda gj: (
                                geojson_utils.geojson_to_file(gj, output_dir=f"tmp/geojson/{args.event_level}")
                                if isinstance(gj, str)
                                else None
                            )
                        )
                        data[col] = data[col].astype(str)

            # change if_exists to "append" to avoid overwriting the database
            # choose "replace" to overwrite the database with a fresh copy of the data
            for i in tqdm(range(len(data))):
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

    if errors.shape != (0, 0):
        from time import time

        tmp_errors_filename = f"tmp/db_insert_errors_{args.event_level}_{args.target_table}_{int(time())}.json"
        logger.error(f"Errors were found! THIS ROW WAS NOT INSERTED! Storing in {tmp_errors_filename}")
        pathlib.Path("tmp").mkdir(parents=True, exist_ok=True)
        errors.to_json(tmp_errors_filename, orient="records")
    connection.close()
