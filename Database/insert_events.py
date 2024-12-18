import argparse
import os
import pathlib
import sqlite3
from typing import Any

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
    event_levels: dict[str, dict[str, str]] = {
        "l1": {"Administrative_Areas": "list"},
        "l2": {"Administrative_Areas": "list"},
        "l3": {"Administrative_Area": "str", "Locations": "list"},
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

    parser.add_argument(
        "-s",
        "--save_output",
        dest="save_output",
        action="store_true",
        help=f"Pass to replace store output. Can be combined with `--dump_geojson_to_file` and `--dry_run`to generate a .parquet copies of the de-duplictaed geojson output without doing any database insertion.",
        required=False,
    )

    parser.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
        help="Pass an output directory for storing the data as identical .parquet files with de-duplicated geojson output.",
        required=False,
    )

    parser.add_argument(
        "-d",
        "--dry_run",
        dest="dry_run",
        action="store_true",
        help="Pass to start a dry run that does not insert anything into the database. Useful with `--save_output`",
        required=False,
    )

    logger = Logging.get_logger(f"database-insertion", level="INFO")
    args = parser.parse_args()
    logger.info(f"ARGS: {args}")
    utils = NormalizeUtils()
    validation = CategoricalValidation()

    if not args.dry_run:
        connection = sqlite3.connect(args.database_name, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = connection.cursor()

    errors = pd.DataFrame()
    files = os.listdir(args.file_dir)
    if args.save_output:
        assert args.output_dir, "Must specify an output directory when `--save_output` is selected"
        pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # levels
    main_level = "l1"
    sub_levels = [x for x in event_levels.keys() if x != "l1"]
    geojson_utils = GeoJsonUtils(nid_path=args.nid_path)

    if args.event_level == main_level:
        args.target_table = "Total_Summary"
        logger.info(f"Processing {main_level}...\n")
        for f in tqdm(files, desc="Files"):
            data = pd.read_parquet(f"{args.file_dir}/{f}", engine="fastparquet")

            # turn invalid currencies to None (for L1 only)
            data = data.parallel_apply(lambda row: validation.validate_currency_monetary_impact(row), axis=1)
            data = data.fillna(float("nan"))

            # geojson in l1 is always of type list
            if args.dump_geojson_to_file:
                for col in event_levels[args.event_level].keys():
                    logger.info(f"Processing GeoJson column {col}_GeoJson in {args.event_level}; File: {f}")

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

            if args.save_output:
                data = data.replace(float("nan"), None)
                data.to_parquet(f"{args.output_dir}/{f}", engine="fastparquet")

            # change if_exists to "append" to avoid overwriting the database
            # choose "replace" to overwrite the database with a fresh copy of the data
            if not args.dry_run:
                for c in [
                    x for x in data.columns if "Area" in x or "Location" in x or "Event_Names" in x or x == "Hazards"
                ]:
                    data[c] = data[c].astype(str)
                    data[c] = data[c].apply(lambda x: x.replace("nan", "None"))

                for i in tqdm(range(len(data)), desc=f"Inserting {f} into {args.database_name}"):
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
        logger.info(f"Processing level {args.event_level}: {args.target_table}...\n")
        if not args.dry_run:
            logger.info(f"Inserting {args.event_level}...\n")
            assert args.target_table, f"When inserting sublevels ({sub_levels}), the target table must be specified!"

            check_table = cursor.execute(
                f"""SELECT name FROM sqlite_master WHERE type='table'
                    AND name='{args.target_table}'; """
            ).fetchall()

            assert len(check_table) == 1, f"Table name {args.target_table} incorrect! Found {check_table} instead."

        for f in tqdm(files, desc="Files"):
            data = pd.read_parquet(f"{args.file_dir}/{f}", engine="fastparquet")
            data = data.fillna(float("nan"))
            if args.dump_geojson_to_file:
                logger.info(f"Popping GeoJson files out for level {args.event_level} and onto disk")
                for col, _type in event_levels[args.event_level].items():
                    eval_type: Any = eval(_type)
                    logger.info(f"Processing GeoJson column {col} in {args.event_level}; File: {f}")
                    if eval_type == list:
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

                    elif eval_type == str:
                        data[f"{col}_GeoJson"] = data.parallel_apply(
                            lambda row: (
                                geojson_utils.geojson_to_file(row[f"{col}_GeoJson"], row[f"{col}_Norm"])
                                if row[f"{col}_GeoJson"]
                                else None
                            ),
                            axis=1,
                        )

            if args.save_output:
                data = data.replace(float("nan"), None)
                data.to_parquet(f"{args.output_dir}/{f}", engine="fastparquet")

            # change if_exists to "append" to avoid overwriting the database
            # choose "replace" to overwrite the database with a fresh copy of the data
            if not args.dry_run:
                for c in [x for x in data.columns if "Area" in x or "Location" in x]:
                    data[c] = data[c].astype(str)
                    data[c] = data[c].apply(lambda x: x.replace("nan", "None"))
                for i in tqdm(range(len(data)), desc=f"Inserting {f} into {args.database_name}"):
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

    if args.dump_geojson_to_file:
        geojson_utils.store_non_english_nids()

    if not args.dry_run:
        if errors.shape != (0, 0):
            from time import time

            tmp_errors_filename = (
                f"{args.error_path}/db_insert_errors_{args.event_level}_{args.target_table}_{int(time())}.json"
            )
            logger.error(f"Insert errors were found! THIS ROW WAS NOT INSERTED! Storing in {tmp_errors_filename}")
            pathlib.Path(args.error_path).mkdir(parents=True, exist_ok=True)
            errors.to_json(tmp_errors_filename, orient="records", indent=3)

        connection.close()
