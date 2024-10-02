import argparse

import pandas as pd

from Database.scr.log_utils import Logging
from Database.scr.normalize_utils import NormalizeUtils

if __name__ == "__main__":
    utils = NormalizeUtils()
    logger = Logging.get_logger("chunk_sys_output", level="INFO")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_filepath",
        dest="input_filepath",
        required=True,
        help="Specifiy the path to the full-run file to break into chunks. Must be a json file!",
        type=str,
    )

    parser.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
        required=True,
        help="Specify the output directory where the .json chunks will be stored.",
        type=str,
    )
    parser.add_argument(
        "-c",
        "--chunk_size",
        dest="chunk_size",
        required=True,
        help="Specify the chunk size",
        type=int,
    )

    args = parser.parse_args()

    logger.info(args)

    try:
        df = pd.read_json(args.input_filepath)
        utils.df_to_json(df, target_dir=args.output_dir, chunk_size=args.chunk_size, orient="records", indent=3)
    except BaseException as err:
        logger.error(f"Could not process file `{args.input_filepath}`. Error: {err}")
        exit()

    logger.info(f"Chunking complete! The json chunks can be found in {args.output_dir}")
