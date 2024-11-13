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
    logger.info("Data loaded!")
    event_id, date_year_suffix = "Event_ID", "_Date_Year"
    admin_areas = "Administrative_Areas"
    admin_area = "Administrative_Area"
    num_min, num_max, num_approx = "Num_Min", "Num_Max", "Num_Approx"

    logger.info("Filling the time gap...")
    for e_id in list(l1[event_id].unique()):
        replace_with_date = (
            l1.loc[l1[event_id] == e_id][[x for x in l1.columns if date_year_suffix in x]].iloc[0].to_dict()
        )
        for level in [l2, l3]:
            for impact in level.keys():
                level[impact][level[impact][event_id] == e_id] = level[impact][level[impact][event_id] == e_id].apply(
                    lambda row: dg_util.fill_date(row, replace_with_date=replace_with_date),
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

    for e_id in list(l1[event_id].unique()):
        for impact in l3.keys():
            l3_areas = l3[impact][(~l3[impact][num_min].isna()) & (l3[impact][event_id] == e_id)][
                f"{admin_area}_Norm"
            ].tolist()

            l2_areas = dg_util.flatten(l2[impact][l2[impact][event_id] == e_id][f"{admin_areas}_Norm"].tolist())

            # check l3 impacts not found in l2
            areas_not_in_l2 = [x for x in l3_areas if x not in l2_areas]
            if areas_not_in_l2:
                for area in areas_not_in_l2:
                    logger.info(
                        f"Administrative Area in l3 missing in l2 found for impact {impact} in Event_ID {e_id}. Area(s): {area}"
                    )
                    l3_rows = l3[impact][
                        (~l3[impact][num_min].isna())
                        & (l3[impact][event_id] == e_id)
                        & (l3[impact][f"{admin_area}_Norm"] == area)
                    ].to_dict(orient="records")
                    for r in l3_rows:
                        new_l2_rows[impact].append(dg_util.l3_to_l2(l3_row=r))

    print(new_l2_rows)
    # TODO: append new_l2_rows
