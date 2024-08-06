import argparse
import pathlib

from scr.normalize_utils import Logging, NormalizeJsonOutput

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

    args = parser.parse_args()

    directory = args.output_file_path.split("/")
    if len(directory) > 1:
        logger.info(f"Creating {'/'.join(directory[:-1])} if it does not exist!")
        pathlib.Path("/".join(directory[:-1])).mkdir(parents=True, exist_ok=True)

    norm = NormalizeJsonOutput()
    norm.normalize_column_names(args.json_file_path, args.output_file_path)
