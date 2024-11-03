import argparse

from Database.scr.normalize_data import DataGapUtils
from Database.scr.normalize_utils import Logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        dest="input_dir",
        help="Provide the llm output directory",
    )

    logger = Logging.get_logger("fill-data-gap", "INFO")
    args = parser.parse_args()
    dg_util = DataGapUtils()
    l1, l2, l3 = dg_util.load_data(input_dir=args.input_dir)
    event_id, date_year_suffix = "Event_ID", "_Date_Year"
    admin_areas = "Administrative_Areas"
    admin_area = "Administrative_Area"

    for event_id in list(l1[event_id].unique()):
        replace_with_date = (
            l1.loc[l1[event_id] == event_id][[x for x in l1.columns if date_year_suffix in x]].iloc[0].to_dict()
        )

        for level in [l2, l3]:
            for impact in level.keys():
                level[impact][level[impact][event_id] == event_id] = level[impact][
                    level[impact][event_id] == event_id
                ].apply(lambda row: dg_util.fill_date(row, replace_with_date=replace_with_date), axis=1)

    for e_id in list(l1[event_id].unique()):
        l1_areas = l1.loc[l1[event_id] == e_id][f"{admin_areas}_Norm"].iloc[0]
        area_col_suffix = ["Norm", "Type", "GID", "GeoJson"]
        l1_target_area_cols = [f"{admin_areas}_{s}" for s in area_col_suffix]

        for impact in l2.keys():
            try:
                l2_series = l2[impact][l2[impact][event_id] == e_id][f"{admin_areas}_Norm"]

                if not l2_series.empty:
                    for n in range(len(l2_series)):
                        l2_areas, l2_idx = {}, []

                        l2_list = l2_series.iloc[n]
                        l2_idx = [l2_list.index(area) for area in l2_list if area not in l1_areas]

                        if l2_idx:
                            logger.info(f"Filling area data gap for Event_ID {e_id} for {impact} at l2")
                            target_area_cols = [f"{admin_areas}_{s}" for s in area_col_suffix]
                            l2_areas = l2[impact][l2[impact][event_id] == e_id][target_area_cols].to_dict(orient="list")
                            for k, v in l2_areas.items():
                                l2_areas[k] = [v[n][idx] for idx in l2_idx]
                            l1.loc[l1[event_id] == e_id][l1_target_area_cols].apply(
                                lambda row: dg_util.fill_area(row, l2_areas, area_col=admin_areas),
                                axis=1,
                            )
            except BaseException as err:
                logger.error(f"Could not fill area data gap for {impact} at l2. Error: {err}")

        for impact in l3.keys():
            try:
                l3_series = l3[impact][l3[impact][event_id] == e_id][f"{admin_area}_Norm"]
                if not l3_series.empty:
                    for n in range(len(l3_series)):
                        l3_area = {}
                        l3_str = l3_series.iloc[n]
                        if isinstance(l3_str, str) and l3_str not in l1_areas:
                            logger.info(f"Filling area data gap for Event_ID {e_id} for {impact} at l3")
                            target_area_cols = [f"{admin_area}_{s}" for s in area_col_suffix]
                            l3_area = l3[impact][l3[impact][event_id] == e_id][target_area_cols].iloc[n].to_dict()
                            for k, v in l3_area.items():
                                l3_area[k] = [v]
                            l1.loc[l1[event_id] == e_id][l1_target_area_cols].apply(
                                lambda row: dg_util.fill_area(row, l3_area, area_col=admin_area),
                                axis=1,
                            )
            except BaseException as err:
                logger.error(f"Could not fill area data gap for {impact} at l3. Error: {err}")
