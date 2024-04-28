import argparse
import os
import sqlite3

import pandas as pd

if __name__ == "__main__":
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
        "-d",
        "--data_path",
        dest="data_path",
        default="Database/output",
        help="""The directory where .parquet files exist so they can be inserted into the db.
        IMPORTANT: Specific event files should start with a 'Specific_' prefix""",
        type=str,
    )

    parser.add_argument(
        "-db",
        "--database_name",
        dest="database_name",
        default="impact.db",
        help="The name of your database (follwed by `.db`)",
        type=str,
    )

    args = parser.parse_args()

    sub_events = [f for f in os.listdir(args.data_path) if f.startswith("Specific_")]
    connection = sqlite3.connect(f"{args.data_path}/{args.database_name}")
    cursor = connection.cursor()

    for i in sub_events:
        df = pd.read_parquet(f"{args.data_path}/{i}")
        sub_event_name = i.split(".")[0]
        # drop _annotation columns
        annotation_colums = [col for col in df.columns if col.endswith("annotation")]
        df = df.drop(columns=annotation_colums)
        # change if_exists to "append" to avoid overwriting the database
        # choose "replace" to overwrite the database with a fresh copy of the data
        df.to_sql(sub_event_name, con=connection, if_exists=args.method, index=False)

    connection.close()
