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

        l1 = pd.read_parquet(l1_filename, engine="fastparquet")
        l1 = norm_utils.replace_nulls(l1).replace({float("nan"): None})
        l2 = {}
        self.logger.info("Loading l2 files...")

        for f, c in tqdm(zip(l2_filenames, l2_categories), desc="L2 files..."):
            try:
                tmp_df = pd.read_parquet(f"{input_dir}/l2/{f}", engine="fastparquet")
                tmp_df = norm_utils.replace_nulls(tmp_df).replace({float("nan"): None})

                l2[c] = tmp_df
                del tmp_df

            except BaseException as err:
                self.logger.error(f"Could not read {input_dir}/l2/{f}. Error: {err}")
        l3 = {}
        self.logger.info("Loading l3 files...")
        for f, c in tqdm(zip(l3_filenames, l3_categories), desc="L3 files..."):
            try:
                tmp_df = pd.read_parquet(f"{input_dir}/l3/{f}", engine="fastparquet")
                tmp_df = norm_utils.replace_nulls(tmp_df).replace({float("nan"): None})

                l3[c] = tmp_df
                del tmp_df

            except BaseException as err:
                self.logger.error(f"Could not read {input_dir}/l3/{f}. Error: {err}")

        return l1, l2, l3

    @staticmethod
    def fill_date(row: dict, replace_with_date: dict):
        date_cols = [x for x in row.keys() if "_Date_" in x]
        if all([True if row[d] is None else False for d in date_cols]):
            for c in date_cols:
                row[c] = replace_with_date[c]
        return row

    @staticmethod
    def fill_area(row: dict, replace_with_area: dict):
        pass

    @staticmethod
    def fill_count(row: dict, replace_with_count: dict):
        pass
