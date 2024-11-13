import pandas as pd

from .log_utils import Logging


class DataGapUtils:
    def __init__(self):
        self.logger = Logging.get_logger("data-gap-utils")

    def load_data(self, input_dir: str) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
        import os

        from tqdm import tqdm

        from Database.scr.normalize_utils import NormalizeUtils

        norm_utils = NormalizeUtils()

        l1_filename = f"{input_dir}/l1"
        l2_filenames = os.listdir(f"{input_dir}/l2")
        l3_filenames = os.listdir(f"{input_dir}/l3")

        l2_categories = [f'{x.split("_Areas_")[-1]}' for x in l2_filenames]
        l3_categories = [f'{x.split("_Area_")[-1]}' for x in l3_filenames]

        self.logger.info("Loading l1 files...")
        l1 = pd.read_parquet(l1_filename, engine="fastparquet")
        l1 = norm_utils.replace_nulls(l1)
        l1.replace({float("nan"): None}, inplace=True)
        l2 = {}
        self.logger.info("Loading l2 files...")

        for f, c in tqdm(zip(l2_filenames, l2_categories), desc="L2 files..."):
            try:
                tmp_df = pd.read_parquet(f"{input_dir}/l2/{f}", engine="fastparquet")
                tmp_df = norm_utils.replace_nulls(tmp_df)
                tmp_df.replace({float("nan"): None}, inplace=True)

                l2[c] = tmp_df
                del tmp_df

            except BaseException as err:
                self.logger.error(f"Could not read {input_dir}/l2/{f}. Error: {err}")
        l3 = {}
        self.logger.info("Loading l3 files...")
        for f, c in tqdm(zip(l3_filenames, l3_categories), desc="L3 files..."):
            try:
                tmp_df = pd.read_parquet(f"{input_dir}/l3/{f}", engine="fastparquet")
                tmp_df = norm_utils.replace_nulls(tmp_df)
                tmp_df.replace({float("nan"): None}, inplace=True)

                l3[c] = tmp_df
                del tmp_df

            except BaseException as err:
                self.logger.error(f"Could not read {input_dir}/l3/{f}. Error: {err}")

        return l1, l2, l3

    @staticmethod
    def fill_date(row: dict, replace_with_date: dict) -> dict:
        year_cols = [x for x in row.keys() if "_Date_Year" in x]
        if all([True if row[d] is None else False for d in year_cols]):
            for c in year_cols:
                row[c] = replace_with_date[c]
        return row

    @staticmethod
    def fill_area(row: dict, missing_areas: dict[str, list], area_col: str) -> dict:
        l1_area_col: str = "Administrative_Areas"
        for c in ["Norm", "Type", "GID"]:
            row[f"{l1_area_col}_{c}"] = row[f"{l1_area_col}_{c}"].extend(missing_areas[f"{area_col}_{c}"])
        return row

    @staticmethod
    def l3_to_l2(l3_row: dict) -> dict:
        l2_row = {}
        for k in l3_row.keys():
            if "Administrative_Area" in k:
                l2_name = k.replace("Area", "Areas")
                l2_row[l2_name] = [l3_row[k]]
                del l2_name
            elif "Location" not in k:
                l2_row[k] = l3_row[k]
        return l2_row

    @staticmethod
    def flatten(xss: list[list]) -> list:
        return [x for xs in xss for x in xs]
