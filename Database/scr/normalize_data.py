import math

import pandas as pd

from .log_utils import Logging


class DataGapUtils:
    def __init__(self):
        self.logger = Logging.get_logger("data-gap-utils")
        self.event_id: str = "Event_ID"
        self.date_year_suffix: str = "_Date_Year"
        self.admin_areas: str = "Administrative_Areas"
        self.admin_area: str = "Administrative_Area"
        self.num_min: str = "Num_Min"
        self.num_max: str = "Num_Max"
        self.num_approx: str = "Num_Approx"
        self.num_unit: str = "Num_Unit"
        self.num_inflation_adjusted: str = "Num_Inflation_Adjusted"
        self.num_inflation_adjusted_year: str = "Num_Inflation_Adjusted_Year"

        self.monetary_categories = ["damage", "insured_damage"]

    @staticmethod
    def safe_isnan(x):
        try:
            return math.isnan(x)
        except:
            return False

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
            p_files = os.listdir(f"{input_dir}/l2/{f}")
            for p_file in p_files:
                try:
                    tmp_df = pd.read_parquet(f"{input_dir}/l2/{f}/{p_file}", engine="fastparquet")
                    tmp_df = norm_utils.replace_nulls(tmp_df)
                    tmp_df.replace({float("nan"): None}, inplace=True)

                    if c not in l2.keys():
                        l2[c] = tmp_df
                    else:
                        l2[c] = pd.concat([l2[c], tmp_df])
                    del tmp_df

                except BaseException as err:
                    self.logger.error(f"Could not read {input_dir}/l2/{f}/{p_file}. Error: {err}")
        l3 = {}
        self.logger.info("Loading l3 files...")
        for f, c in tqdm(zip(l3_filenames, l3_categories), desc="L3 files..."):
            p_files = os.listdir(f"{input_dir}/l3/{f}")
            for p_file in p_files:
                try:
                    tmp_df = pd.read_parquet(f"{input_dir}/l3/{f}/{p_file}", engine="fastparquet")
                    tmp_df = norm_utils.replace_nulls(tmp_df)
                    tmp_df.replace({float("nan"): None}, inplace=True)

                    if c not in l3.keys():
                        l3[c] = tmp_df
                    else:
                        l3[c] = pd.concat([l3[c], tmp_df])
                    del tmp_df

                except BaseException as err:
                    self.logger.error(f"Could not read {input_dir}/l3/{f}/{p_file}. Error: {err}")

        self.logger.info("Converting any bytes to str for l1")
        for col in l1.columns:
            l1[col] = l1[col].apply(lambda x: str(x) if isinstance(x, bytes) else x)

        self.logger.info("Converting any bytes to str for l2")
        for impact in l2.keys():
            for col in l2[impact].columns:
                l2[impact][col] = l2[impact][col].apply(lambda x: str(x) if isinstance(x, bytes) else x)

        self.logger.info("Converting any bytes to str for l3")
        for impact in l3.keys():
            for col in l3[impact].columns:
                l3[impact][col] = l3[impact][col].apply(lambda x: str(x) if isinstance(x, bytes) else x)

        return l1, l2, l3

    def fill_date(self, row: pd.DataFrame, replace_with_date: dict, impact: str) -> pd.DataFrame:
        if all([True if (row[d] is None or self.safe_isnan(row[d])) else False for d in [self.s_y, self.e_y]]):
                if replace_with_date[c] is not None and not self.safe_isnan(replace_with_date[c]):
                    row[c] = replace_with_date[c]
                    self.logger.info(
                        f"Filling year {replace_with_date[c]} for {row[self.event_id]} record for impact {impact} in column {c} for level {'l2' if 'Administrative_Areas_Norm' in dict(row).keys() else 'l3'}"
                    )
        return row

    def fill_area(self, row: pd.DataFrame, missing_areas: dict[str, list], area_col: str) -> pd.DataFrame:
        for c in ["Norm", "Type", "GID", "GeoJson"]:
            row[f"{self.admin_areas}_{c}"] = row[f"{self.admin_areas}_{c}"].extend(missing_areas[f"{area_col}_{c}"])
        return row

    def l2_to_l1(
        self, row: pd.DataFrame, agg_min: float, agg_max: float, impact: str, e_id: str, unit=None, ia=None, ia_year=None
    ) -> pd.DataFrame:
        total_min, total_max, total_approx = f"Total_{impact}_Min", f"Total_{impact}_Max", f"Total_{impact}_Approx"

        total_unit, total_ia, total_ia_year = (
            f"Total_{impact}_Unit",
            f"Total_{impact}_Inflation_Adjusted",
            f"Total_{impact}_Inflation_Adjusted_Year",
        )
        original_row = row.copy()

        changed_min, changed_max = False, False
        if any([row[total_min] == None, self.safe_isnan(row[total_min]), row[total_min] < agg_min]):
            row[total_min] = agg_min
            changed_min = True
        if any([row[total_max] == None, self.safe_isnan(row[total_max]), row[total_max] < agg_max]):
            row[total_max] = agg_max
            changed_max = True
        if changed_min or changed_max:
            self.logger.info(
                f"Discrepancy between l2 and l1 found in {e_id} in {total_min}-{total_max}; L1: {original_row[total_min]}-{original_row[total_max]}; L2 (aggregated): {agg_min}-{agg_max}."
            )
            row[total_approx] = 1
            if impact.lower() in self.monetary_categories:
                row[total_unit] = unit if unit else row[total_unit]
                row[total_ia] = ia if ia else row[total_ia]
                row[total_ia_year] = ia_year if ia_year else row[total_ia_year]
                if unit or ia or ia_year:
                    self.logger.info(
                        f"Discrepancy between l2 and l1 found in {e_id} in {total_unit}, {total_ia}, and {total_ia_year}; L1: {original_row[total_unit]}, {original_row[total_ia]}, and {original_row[total_ia_year]}; L2: {row[total_unit]}, {row[total_ia]}, and {row[total_ia_year]}"
                    )
        return row

    def l3_to_l2(self, l3_row: pd.DataFrame) -> dict:
        l2_row = {}
        for k in l3_row.keys():
            if self.admin_area in k:
                l2_name = k.replace("Area", "Areas")
                l2_row[l2_name] = [l3_row[k]]
                del l2_name
            elif "Location" not in k:
                l2_row[k] = l3_row[k]
        return l2_row

    @staticmethod
    def flatten(xss: list[list]) -> list:
        return [x for xs in xss for x in xs]

    def check_impacts(self, l2_row: pd.DataFrame, l3_row: pd.DataFrame, impact: str) -> dict | pd.DataFrame:
        try:
            l2_aa = l2_row[f"{self.admin_areas}_Norm"][0]
            if impact.lower() in self.monetary_categories:
                l3_tgt_row = l3_row[l3_row[f"{self.admin_area}_Norm"] == l2_aa][
                    [
                        f"{self.admin_area}_Norm",
                        self.num_min,
                        self.num_max,
                        self.num_unit,
                        self.num_inflation_adjusted,
                        self.num_inflation_adjusted_year,
                    ]
                ].reset_index()
            else:
                l3_tgt_row = l3_row[l3_row[f"{self.admin_area}_Norm"] == l2_aa][
                    [f"{self.admin_area}_Norm", self.num_min, self.num_max]
                ].reset_index()

            new_l2_row = l2_row.copy()
            # TODO: lift monetary category exception after applying inflation adjustment and conversion!
            if (not l3_tgt_row.empty) and (impact.lower() not in self.monetary_categories):
                for i in (self.num_min, self.num_max):
                    if l3_tgt_row[i][0] is not None:
                        if l2_row[i] is None:
                            new_l2_row[i] = l3_tgt_row[i][0]
                            self.logger.info(
                                f"Discrepancy in {i} found at {l2_row[self.event_id]} for impact {impact}: {l2_row[i]} vs {l3_tgt_row[i][0]} (l2 vs l3)"
                            )
                        else:
                            if l2_row[i] < l3_tgt_row[i][0] and impact not in self.monetary_categories:
                                new_l2_row[i] = l3_tgt_row[i][0]
                                self.logger.info(
                                    f"Discrepancy in {i} found at {l2_row[self.event_id]} for impact {impact}: {l2_row[i]} vs {l3_tgt_row[i][0]} (l2 vs l3)"
                                )

                if dict(l2_row) != dict(new_l2_row):
                    new_l2_row[self.num_approx] = 1

                    # in case of any updates to l2, transfer monetary impact values upwards (l3->l2)
                    if impact.lower() in self.monetary_categories:
                        self.logger.info(
                            f"""Updating `{self.num_unit} ({new_l2_row[self.num_unit]} -> {l3_tgt_row[self.num_unit][0]})`, `{self.num_inflation_adjusted} ({new_l2_row[self.num_inflation_adjusted]} -> {l3_tgt_row[self.num_inflation_adjusted][0]})`, and `{self.num_inflation_adjusted_year}({new_l2_row[self.num_inflation_adjusted_year]} -> {l3_tgt_row[self.num_inflation_adjusted_year][0]})` at {l2_row[self.event_id]} for monetary impact {impact}"""
                        )
                        new_l2_row[self.num_unit] = l3_tgt_row[self.num_unit][0]
                        new_l2_row[self.num_inflation_adjusted] = l3_tgt_row[self.num_inflation_adjusted][0]
                        new_l2_row[self.num_inflation_adjusted_year] = l3_tgt_row[self.num_inflation_adjusted_year][0]
        except:
            self.logger.error(
                f"Could not check impacts because Area list is empty: {l2_row[f'{self.admin_areas}_Norm']}. No changes were applied to the row: {dict(l2_row)}"
            )
            return l2_row
        return new_l2_row
