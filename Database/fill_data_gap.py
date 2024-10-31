import argparse

from Database.scr.normalize_data import DataGapUtils

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        dest="input_dir",
        help="Provide the llm output directory",
    )

    args = parser.parse_args()
    dg_util = DataGapUtils()
    l1, l2, l3 = dg_util.load_data(input_dir=args.input_dir)
    event_id, date_year_suffix = "Event_ID", "_Date_Year"

    for event_id in list(l1[event_id].unique()):
        replace_with_date = (
            l1.loc[l1[event_id] == event_id][[x for x in l1.columns if date_year_suffix in x]].iloc[0].to_dict()
        )

        for level in [l2, l3]:
            for impact in level.keys():
                level[impact][level[impact][event_id] == event_id] = level[impact][
                    level[impact][event_id] == event_id
                ].apply(lambda row: dg_util.fill_date(row, replace_with_date=replace_with_date), axis=1)
