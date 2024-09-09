import argparse
import os
import pathlib
import sqlite3

import pandas as pd
from tqdm import tqdm

from Database.scr.normalize_utils import Logging

if __name__ == "__main__":
    event_levels = {
        "l1": "Total_Summary",
        "l2": "Instance_Per_Administrative_Areas_",
        "l3": "Specific_Instance_Per_Administrative_Area_",
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

    args = parser.parse_args()
    logger = Logging.get_logger(f"insert {args.event_level} to {args.database_name}", level="INFO")

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
            # change if_exists to "append" to avoid overwriting the database
            # choose "replace" to overwrite the database with a fresh copy of the data
        for i in tqdm(range(len(data))):
            try:
                data.iloc[i : i + 1].to_sql(name=args.target_table, con=connection, if_exists=args.method, index=False)
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
            # change if_exists to "append" to avoid overwriting the database
            # choose "replace" to overwrite the database with a fresh copy of the data
            for i in tqdm(range(len(data))):
                try:
                    data.iloc[i : i + 1].to_sql(
                        name=args.target_table, con=connection, if_exists=args.method, index=False
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
