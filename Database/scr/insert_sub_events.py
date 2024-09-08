import argparse
import os
import sqlite3

import pandas as pd

# TODO: adapt for inserting l2 and l3
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
        default="Database/output/dev",
        help="""The directory where .parquet files exist so they can be inserted into the db.
        IMPORTANT: Specific event files should start with a 'Specific_' prefix""",
        type=str,
    )

    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        help="The name of the parquet file in the <DATA_PATH> directory",
        type=str,
        required=False,
    )

    parser.add_argument(
        "-db",
        "--database_name",
        dest="database_name",
        default="impact.v0.db",
        help="The name of your database (followed by the extension name, such as ´.db´)",
        type=str,
    )

    args = parser.parse_args()
    if args.filename:
        sub_events = [args.filename]
    else:
        sub_events = [f for f in os.listdir(args.data_path) if (f.startswith("Specific_") and f.endswith(".parquet"))]

    connection = sqlite3.connect(args.database_name)
    cursor = connection.cursor()

    for i in sub_events:
        df = pd.read_parquet(f"{args.data_path}/{i}")
        sub_event_name = i.split(".")[0]
        # drop _annotation columns
        annotation_columns = [col for col in df.columns if col.endswith("annotation")]
        df = df.drop(columns=annotation_columns)
        # change if_exists to "append" to avoid overwriting the database
        # choose "replace" to overwrite the database with a fresh copy of the data
        df.to_sql(sub_event_name, con=connection, if_exists=args.method, index=False)

    connection.close()
