import argparse
import pathlib
from scr.normalize_utils import Logging, NormalizeJsonOutput

if __name__ == "__main__":
    logger = Logging.get_logger("merge-mixtral-or-mistral-output")
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input_dir",
        dest="input_dir",
        help="Choose the input dir. Directory should contain json files where the filename is the name of the event.",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
        help="Choose an output dir. Directory must already exist.",
        type=str,
    )

    parser.add_argument(
        "-m",
        "--model_name",
        dest="model_name",
        help="The name of the model to use as the json output filename. Defaults to 'events'.",
        type=str,
        default="event",
    )

    args = parser.parse_args()
    logger.info(args)

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True) 

    json_utils = NormalizeJsonOutput()
    dfs = json_utils.merge_json(args.input_dir)
    filename = json_utils.save_json(dfs, model_name=args.model_name, output_dir=args.output_dir)
    logger.info(f"JSON files merged and normalzied. Find the file in {filename}")
