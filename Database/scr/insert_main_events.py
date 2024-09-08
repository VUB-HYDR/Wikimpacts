import argparse
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
        default="Database/output/dev",
        help="The directory where .parquet files exist so they can be inserted into the db",
        type=str,
    )

    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        default="response_wiki_GPT4_20240327_eventNo_1_8_all_category.parquet",
        help="The name of the parquet file in the <DATA_PATH> directory",
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

    args = parser.parse_args()
    data = pd.read_parquet(f"{args.data_path}/{args.filename}")

    connection = sqlite3.connect(args.database_name)
    cursor = connection.cursor()

    # change if_exists to "append" to avoid overwriting the database
    # choose "replace" to overwrite the database with a fresh copy of the data
    data.to_sql("Total_Summary_Events", con=connection, if_exists=args.method, index=False)

    connection.close()
