import argparse
import pathlib

import pandas as pd

from Database.scr.normalize_data import DataGapUtils
from Database.scr.normalize_utils import Logging, NormalizeUtils

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        dest="input_dir",
        help="Provide the llm input directory",
    )

    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        dest="output_dir",
        help="Provide the llm output directory",
    )

    logger = Logging.get_logger("fill-data-gap", "INFO", "data_gap.log")
    args = parser.parse_args()
    dg_utils = DataGapUtils()
    norm_utils = NormalizeUtils()

    l1, l2, l3 = dg_utils.load_data(input_dir=args.input_dir)
    event_ids = list(l1[dg_utils.event_id].unique())
    logger.info("Data loaded!")

    logger.info("Filling the time (year) gap...")
    for e_id in event_ids:
        replace_with_date = (
            l1.loc[l1[dg_utils.event_id] == e_id][[x for x in l1.columns if dg_utils.date_year_suffix in x]]
            .iloc[0]
            .to_dict()
        )
        for level in [l2, l3]:
            for impact in level.keys():
                level[impact][level[impact][dg_utils.event_id] == e_id] = level[impact][
                    level[impact][dg_utils.event_id] == e_id
                ].apply(
                    lambda row: dg_utils.fill_date(row, replace_with_date=replace_with_date),
                    axis=1,
                )

    # Replace NaNs will NoneType
    for level in [l2, l3]:
        for impact in level.keys():
            level[impact].replace(float("nan"), None, inplace=True)

    logger.info("Filling impacts upward (l3->l2) if an l3 administrative area is missing from l2")
    new_l2_rows: dict[str, list] = {
        "Affected": [],
        "Buildings_Damaged": [],
        "Damage": [],
        "Deaths": [],
        "Displaced": [],
        "Homeless": [],
        "Injuries": [],
        "Insured_Damage": [],
    }

    for e_id in event_ids:
        for impact in l3.keys():
            l3_areas = l3[impact][l3[impact][dg_utils.event_id] == e_id][f"{dg_utils.admin_area}_Norm"].tolist()

            l2_areas = dg_utils.flatten(
                l2[impact][l2[impact][dg_utils.event_id] == e_id][f"{dg_utils.admin_areas}_Norm"].tolist()
            )

            # check l3 impacts not found in l2
            areas_not_in_l2 = [x for x in l3_areas if x not in l2_areas]
            if areas_not_in_l2:
                for area in areas_not_in_l2:
                    logger.info(
                        f"Administrative Area in l3 missing in l2 found for impact {impact} in Event_ID {e_id}. Area(s): {area}"
                    )
                    l3_rows = l3[impact][
                        (l3[impact][dg_utils.event_id] == e_id) & (l3[impact][f"{dg_utils.admin_area}_Norm"] == area)
                    ].to_dict(orient="records")
                    for r in l3_rows:
                        new_l2_rows[impact].append(dg_utils.l3_to_l2(l3_row=r))

    logger.info("Appending l3->l2 impact data...")
    for impact in [x for x in list(new_l2_rows.keys()) if x in list(l2.keys())]:
        l2[impact] = pd.concat([l2[impact], pd.DataFrame(new_l2_rows[impact])])

    logger.info("Comparing impacts between l3 and l2 and using l3 values if they are larger than l2")
    for e_id in event_ids:
        for impact in l3.keys():
            cols = [f"{dg_utils.admin_area}_Norm", dg_utils.num_min, dg_utils.num_max, dg_utils.num_approx]
            if impact.lower() in dg_utils.monetary_categories:
                cols.extend([dg_utils.num_unit, dg_utils.num_inflation_adjusted, dg_utils.num_inflation_adjusted_year])

            # check if l3 impact values > l2 impact values
            l3[impact][cols] = l3[impact][cols].replace({None: float("nan")})
            l3_impacts = (
                l3[impact][(l3[impact][dg_utils.event_id] == e_id) & (~l3[impact][dg_utils.num_min].isna())][cols]
                .groupby(f"{dg_utils.admin_area}_Norm", as_index=False, dropna=True)
                .sum()
            )
            l2[impact][l2[impact][dg_utils.event_id] == e_id] = l2[impact][l2[impact][dg_utils.event_id] == e_id].apply(
                lambda row: dg_utils.check_impacts(l2_row=row, l3_row=l3_impacts, impact=impact), axis=1
            )

    # Replace NaNs will NoneType
    for level in [l2, l3]:
        for impact in level.keys():
            level[impact].replace(float("nan"), None, inplace=True)

    logger.info("Appending areas from l2/l3 to l1 if missing")
    for e_id in event_ids:
        l1_areas = l1.loc[l1[dg_utils.event_id] == e_id][f"{dg_utils.admin_areas}_Norm"].iloc[0]
        area_col_suffix = ["Norm", "Type", "GID", "GeoJson"]
        l1_target_area_cols = [f"{dg_utils.admin_areas}_{s}" for s in area_col_suffix]

        for impact in l2.keys():
            try:
                l2_series = l2[impact][l2[impact][dg_utils.event_id] == e_id][f"{dg_utils.admin_areas}_Norm"]

                if not l2_series.empty:
                    for n in range(len(l2_series)):
                        l2_areas, l2_idx = {}, []

                        l2_list = l2_series.iloc[n]
                        l2_idx = [l2_list.index(area) for area in l2_list if area not in l1_areas]

                        if l2_idx:
                            target_area_cols = [f"{dg_utils.admin_areas}_{s}" for s in area_col_suffix]
                            l2_areas = l2[impact][l2[impact][dg_utils.event_id] == e_id][target_area_cols].to_dict(
                                orient="list"
                            )

                            for k, v in l2_areas.items():
                                l2_areas[k] = [v[n][idx] for idx in l2_idx]
                            logger.info(
                                f"Filling area data gap for Event_ID {e_id} for {impact} at l2->l1. Area(s): {l2_areas[f'{dg_utils.admin_areas}_Norm']}"
                            )
                            l1.loc[l1[dg_utils.event_id] == e_id][l1_target_area_cols].apply(
                                lambda row: dg_utils.fill_area(row, l2_areas, area_col=dg_utils.admin_areas),
                                axis=1,
                            )
            except BaseException as err:
                logger.error(f"Could not fill area data gap for {impact} at l2. Error: {err}")

        for impact in l3.keys():
            try:
                l3_series = l3[impact][l3[impact][dg_utils.event_id] == e_id][f"{dg_utils.admin_area}_Norm"]
                if not l3_series.empty:
                    for n in range(len(l3_series)):
                        l3_area = {}
                        l3_str = l3_series.iloc[n]
                        if isinstance(l3_str, str) and l3_str not in l1_areas:
                            logger.info(f"Filling area data gap for Event_ID {e_id} for {impact} at l3->l1")
                            target_area_cols = [f"{dg_utils.admin_area}_{s}" for s in area_col_suffix]
                            l3_area = (
                                l3[impact][l3[impact][dg_utils.event_id] == e_id][target_area_cols].iloc[n].to_dict()
                            )
                            for k, v in l3_area.items():
                                l3_area[k] = [v]
                            l1.loc[l1[dg_utils.event_id] == e_id][l1_target_area_cols].apply(
                                lambda row: dg_utils.fill_area(row, l3_area, area_col=dg_utils.admin_area),
                                axis=1,
                            )
            except BaseException as err:
                logger.error(f"Could not fill area data gap for {impact} at l3. Error: {err}")

    logger.info("Filling data gap upwards (l2 -> l1) for NULL impacts")
    for impact in l2.keys():
        empty_l1_events = l1[
            [dg_utils.event_id, f"Total_{impact}_Min", f"Total_{impact}_Max", f"Total_{impact}_Approx"]
        ][l1[f"Total_{impact}_Min"].isna()][dg_utils.event_id].unique()
        for e_id in empty_l1_events:
            impact_per_event_id = l2[impact][[dg_utils.num_min, dg_utils.num_max]][
                l2[impact][dg_utils.event_id] == e_id
            ]
            if not impact_per_event_id.empty:
                agg_min, agg_max = impact_per_event_id.sum()
                unit, ia, ia_year = None, None, None

                if impact.lower() in dg_utils.monetary_categories:
                    monetary_impacts = l2[impact][
                        (l2[impact][dg_utils.event_id] == e_id) & (~l2[impact][dg_utils.num_unit].isna())
                    ][
                        [dg_utils.num_unit, dg_utils.num_inflation_adjusted, dg_utils.num_inflation_adjusted_year]
                    ].reset_index()

                    if not monetary_impacts.empty:
                        # assumes all currencies/inflation adjustment/year are identical, grabs the first only
                        unit, ia, ia_year = (
                            monetary_impacts[dg_utils.num_unit][0],
                            monetary_impacts[dg_utils.num_inflation_adjusted][0],
                            monetary_impacts[dg_utils.num_inflation_adjusted_year][0],
                        )

                l1[l1[dg_utils.event_id] == e_id] = l1[l1[dg_utils.event_id] == e_id].apply(
                    lambda row: dg_utils.l2_to_l1(row, agg_min, agg_max, impact, e_id, unit, ia, ia_year), axis=1
                )

    # Replace NaNs will NoneType
    for level in [l2, l3]:
        for impact in level.keys():
            level[impact].replace(float("nan"), None, inplace=True)

    logger.info(f"Storing results in {args.output_dir}")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    l1_output_dir = f"{args.output_dir}/l1"
    pathlib.Path(l1_output_dir).mkdir(parents=True, exist_ok=True)

    norm_utils.df_to_parquet(l1, l1_output_dir, 25, object_encoding="json")

    for impact in l2.keys():
        l2_output_dir = f"{args.output_dir}/l2/Instance_Per_Administrative_Areas_{impact}"
        pathlib.Path(l2_output_dir).mkdir(parents=True, exist_ok=True)

        norm_utils.df_to_parquet(l2[impact], l2_output_dir, 25, object_encoding="json")

    for impact in l3.keys():
        l3_output_dir = f"{args.output_dir}/l3/Specific_Instance_Per_Administrative_Area_{impact}"
        pathlib.Path(l3_output_dir).mkdir(parents=True, exist_ok=True)
        norm_utils.df_to_parquet(l3[impact], l3_output_dir, 25, object_encoding="json")

    logger.info("Done!")
