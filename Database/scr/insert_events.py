import argparse
import os
import sqlite3

import pandas as pd

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
        dest="--event_level",
        required=True,
        help="The event level to parse. Pass only 1",
        choices=event_levels.keys(),
        type=str,
    )

    parser.add_argument(
        "-t",
        "--target_table",
        dest="--target_table",
        default=None,
        required=False,
        help="Must be a table in the target database. Example: `Instance_Per_Administrative_Areas_Deaths`. For l2 and l3 only!",
        type=str,
    )

    args = parser.parse_args()
    connection = sqlite3.connect(args.database_name)
    cursor = connection.cursor()
    files = os.listdir(args.file_dir)

    # levels
    main_level = "l1"
    sub_levels = [x for x in event_levels.keys() if x != "l1"]

    if args.event_level == main_level:
        for f in files:
            data = pd.read_parquet(f, engine="fastparquet")
            # change if_exists to "append" to avoid overwriting the database
            # choose "replace" to overwrite the database with a fresh copy of the data
            data.to_sql("Total_Summary", con=connection, if_exists=args.method, index=False)

    elif args.event_level in sub_levels:
        assert args.target_table, f"When inserting sublevels ({sub_levels}), the target table must be specified!"

        check_table = cursor.execute(
            f"""SELECT tableName FROM sqlite_master WHERE type='table'
                AND tableName='{args.target_table}'; """
        ).fetchall()

        assert len(check_table) == 1, f"Table name {args.target_table} incorrect! Found {check_table} instead."

        for f in files:
            data = pd.read_parquet(f, engine="fastparquet")
            # change if_exists to "append" to avoid overwriting the database
            # choose "replace" to overwrite the database with a fresh copy of the data
            data.to_sql(args.target_table, con=connection, if_exists=args.method, index=False)

    connection.close()
