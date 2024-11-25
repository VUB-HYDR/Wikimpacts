import argparse
import json
import os
import sqlite3

import pandas as pd
from tqdm import tqdm

from Database.scr.normalize_utils import Logging

tqdm.pandas()

logger = Logging.get_logger("create_geojson_tbl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-db",
        "--database",
        dest="database",
        help="Path to sqlite database",
        required=True,
        type=str,
    )

    parser.add_argument(
        "-tbl",
        "--table_schema",
        dest="table_schema",
        help="Specify the table schema file",
        required=True,
        type=str,
    )

    parser.add_argument(
        "-f",
        "--file_path",
        dest="file_path",
        help="Path to .json files to be inserted",
        required=True,
        type=str,
    )

    args = parser.parse_args()
    parser = argparse.ArgumentParser()
    connection = sqlite3.connect(args.database, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = connection.cursor()

    logger.info(f"Database {args.database}")
    # create table if it does not exist (does not affect existing data)
    with open(args.table_schema, "r") as f:
        generate_database_command = f.read()

    commands = generate_database_command.split(";")
    commands = [i for i in commands if i.strip()]

    for i in commands:
        if i:
            logger.info(f"Executing DB command:\n{i}")
            try:
                cursor.execute(i)
            except sqlite3.Error as err:
                logger.error(f"Could not create table. {type(err).__name__}: {err}")

    # insert files into database
    files = [f"{args.file_path}/{x}" for x in os.listdir(args.file_path) if x.endswith(".json")]
    filenames = [x.split(".json")[0].split("/")[-1] for x in files]
    data = pd.DataFrame(columns=["nid", "geojson_obj"])
    logger.info(f"Found {len(filenames)} files")

    for i in tqdm(range(len(files))):
        with open(files[i]) as f:
            geojson_obj = json.dumps(json.load(f))
            binary_data = bytes(geojson_obj, "utf-8")
            row = pd.DataFrame(data={"nid": filenames[i], "geojson_obj": binary_data}, index=[0])
            data = pd.concat(
                [data, row],
                ignore_index=True,
            )
    errors = None
    for i in tqdm(range(len(data))):
        try:
            data.iloc[i : i + 1].to_sql(
                name="GeoJson_Obj",
                con=connection,
                if_exists="append",
                index=False,
            )
        except sqlite3.IntegrityError as err:
            logger.error(
                f"""Could not insert event for level {args.event_level}. Error {err}.
                             The problematic row will be stored in /tmp/ with the error. GeoJson columns will not be included."""
            )
            err_row = data.iloc[i : i + 1].copy()
            err_row["ERROR"] = err
            errors = pd.concat([errors, err_row], ignore_index=True)

    if errors:
        logger.error(f"Insert errors:\n{errors['nid'].tolist()}")
