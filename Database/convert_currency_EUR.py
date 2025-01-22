import argparse
import pathlib
from datetime import datetime

from Database.scr.normalize_currency import CurrencyConversion, InflationAdjustment
from Database.scr.normalize_data import DataUtils
from Database.scr.normalize_utils import Logging, NormalizeUtils

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        dest="input_dir",
        help="Provide the llm data gap fixed with USD directory",
    )

    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        dest="output_dir",
        help="Provide the llm output with EUR directory",
    )
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    logger = Logging.get_logger("USD to EUR in inflation year", "DEBUG", f"USD_EUR_{timestamp}.log")
    args = parser.parse_args()

    data_utils = DataUtils()
    norm_utils = NormalizeUtils()
    ia_utils = InflationAdjustment()
    cc_utils = CurrencyConversion()
    l1, l2, l3 = data_utils.load_data(input_dir=args.input_dir)
    logger.info("Data loaded!")
    logger.info("Converting USD to EUR")
    for cat in ia_utils.monetary_categories:
        logger.info(f"Converting currencies in L1 for category {cat}")
        l1 = l1.apply(lambda x: cc_utils.Convert_USD_to_EUR(x, l1_impact=cat, level="l1", impact=cat), axis=1)
        logger.info(f"Converting currencies in L2 for category {cat}")
        l2[cat] = l2[cat].apply(
            lambda x: cc_utils.Convert_USD_to_EUR(x, l1_impact=None, level="l2", impact=cat), axis=1
        )
        logger.info(f"Converting currencies in L3 for category {cat}")
        l3[cat] = l3[cat].apply(
            lambda x: cc_utils.Convert_USD_to_EUR(x, l1_impact=None, level="l3", impact=cat), axis=1
        )

    logger.info(f"Storing results in {args.output_dir}")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    l1_output_dir = f"{args.output_dir}/l1"
    pathlib.Path(l1_output_dir).mkdir(parents=True, exist_ok=True)
    l1 = l1[~l1.astype(str).duplicated()]
    l1 = l1.replace(float("nan"), None)
    norm_utils.df_to_parquet(l1, l1_output_dir, 25, object_encoding="json", index=False)

    for impact in l2.keys():
        l2_output_dir = f"{args.output_dir}/l2/Instance_Per_Administrative_Areas_{impact}"
        pathlib.Path(l2_output_dir).mkdir(parents=True, exist_ok=True)
        l2[impact] = l2[impact][~l2[impact].astype(str).duplicated()]
        l2[impact] = l2[impact].replace(float("nan"), None)
        norm_utils.df_to_parquet(l2[impact], l2_output_dir, 25, object_encoding="json", index=False)

    for impact in l3.keys():
        l3_output_dir = f"{args.output_dir}/l3/Specific_Instance_Per_Administrative_Area_{impact}"
        pathlib.Path(l3_output_dir).mkdir(parents=True, exist_ok=True)
        l3[impact] = l3[impact][~l3[impact].astype(str).duplicated()]
        l3[impact] = l3[impact].replace(float("nan"), None)
        norm_utils.df_to_parquet(l3[impact], l3_output_dir, 25, object_encoding="json", index=False)

    logger.info("Done!")
