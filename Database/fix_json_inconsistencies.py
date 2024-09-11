import argparse
import pathlib

from Database.scr.log_utils import Logging
from Database.scr.normalize_utils import NormalizeJsonOutput

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    logger = Logging.get_logger("fix nested json sys output")

    parser.add_argument(
        "-i",
        "--json_file_path",
        dest="json_file_path",
        help="The full path to the json file to fix",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output_file_path",
        dest="output_file_path",
        help="The full output path, including the name and extension of the file",
        type=str,
    )

    parser.add_argument(
        "-n",
        "--normalize",
        dest="normalize",
        help="Which inconsistency type to normalize",
        choices=["nested time fields", "list of nums"],
        required=True,
        type=str,
    )

    args = parser.parse_args()
    logger.info(f"Correcting: {args.normalize}")

    directory = args.output_file_path.split("/")
    if len(directory) > 1:
        logger.info(f"Creating {'/'.join(directory[:-1])} if it does not exist!")
        pathlib.Path("/".join(directory[:-1])).mkdir(parents=True, exist_ok=True)

    norm = NormalizeJsonOutput()
    if args.normalize == "nested time fields":
        norm.normalize_column_names(args.json_file_path, args.output_file_path)
    if args.normalize == "list of nums":
        norm.normalize_lists_of_num(args.json_file_path, args.output_file_path, locale_config="en_US.UTF-8")
