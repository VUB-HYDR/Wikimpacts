import argparse
import ast
import json
import pathlib
from pprint import pformat

import pandas as pd

from Database.scr.normalize_utils import NormalizeUtils
from Evaluation.comparer import Comparer
from Evaluation.matcher import CurrencyMatcher, SpecificInstanceMatcher
from Evaluation.utils import Logging
from Evaluation.weights import weights as weights_dict

pd.options.display.max_rows = 999

if __name__ == "__main__":
    logger = Logging.get_logger("evaluator")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-sys",
        "--sys_output",
        dest="system_output",
        help="The full path to the system output in parquet",
        type=str,
    )

    parser.add_argument(
        "-gold",
        "--gold_set",
        dest="gold_set",
        help="The full path to the gold set in parquet",
        type=str,
    )

    parser.add_argument(
        "-m",
        "--model_name",
        dest="model_name",
        help="A model name to store the results",
        type=str,
    )

    parser.add_argument(
        "-null",
        "--null_penalty",
        dest="null_penalty",
        default=1,
        help="Null penalty, defaults to 1",
        type=float,
    )

    parser.add_argument(
        "-s",
        "--score",
        dest="score",
        default="all",
        choices=["wikipedia", "artemis", "all"],
        help="Which event source to use for evaluation.",
        type=str,
    )

    parser.add_argument(
        "-w",
        "--weights_config",
        dest="weights_config",
        default="all_columns",
        choices=weights_dict.keys(),
        help="Which weights configuration to use. Weight configs are found in `weights.py` in this same directory",
        type=str,
    )

    parser.add_argument(
        "-lvl",
        "--event_level",
        dest="event_level",
        choices=["l1", "l2", "l3"],
        help="Choose which events to parse. Possible values: main or sub",
        type=str,
        required=True,
    )

    parser.add_argument(
        "-si",
        "--impact_type",
        dest="impact_type",
        help="""Supply the specific instance type/category (example: 'deaths', 'insurance_damage')
            to store matched specific instances for gold and sys""",
        type=str,
        required=False,
    )

    parser.add_argument(
        "-mn",
        "--matcher_null_penalty",
        dest="matcher_null_penalty",
        default=0.5,
        help="""Specify the null penalty for matching l2 and l3 events""",
        type=float,
        required=True,
    )

    parser.add_argument(
        "-mt",
        "--matcher_threshold",
        dest="matcher_threshold",
        default=0.6,
        help="""Specify the threshold for matching l2 and l3 events""",
        type=float,
        required=True,
    )

    args = parser.parse_args()
    utils = NormalizeUtils()
    output_dir = f"Database/evaluation_results/{args.model_name}"
    logger.info(f"Creating {output_dir} if it does not exist!")
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

    matcher = SpecificInstanceMatcher(null_penalty=args.matcher_null_penalty, threshold=args.matcher_threshold)

    try:
        gold = pd.read_parquet(args.gold_set, engine="fastparquet").replace(
            {float("nan"): None, "NULL ": None, "NULL": None, "None": None}
        )

        sys_f = pathlib.Path(args.system_output)
        if sys_f.is_dir():
            logger.info(
                f"""The provided system output path is to a directory `{args.system_output}`.
                If .parquet files are present, they will be pulled and concatenated into a single file."""
            )
            logger.info(f"Files in {args.system_output}: {list(sys_f.iterdir())}")

        sys = pd.read_parquet(args.system_output, engine="fastparquet").replace(
            {float("nan"): None, "NULL ": None, "NULL": None, "None": None}
        )

    except BaseException as err:
        logger.error(f"Loading the gold or sys files unsuccessful. Error: {err}")
        exit()

    for _set in [gold, sys]:
        for c in [_c for _c in _set.columns if "Areas" in _c or "Locations" in _c]:
            _set[c] = _set[c].apply(utils.eval)

    admin_area_columns = [
        "Administrative_Area_Norm",
        "Administrative_Areas_Norm",
        "Country_Norm",
    ]
    location_columns = ["Location_Norm", "Locations_Norm"]
    any_area_columns = admin_area_columns + location_columns

    if args.event_level in ["l2", "l3"]:
        logger.info(f"Pairing up {args.event_level} events")
        event_ids = set(list(gold.Event_ID.unique()) + list(sys.Event_ID.unique()))
        si_gold, si_sys = [], []
        for gold_list, sys_list in zip(
            [
                gold[gold.Event_ID == e_id][weights_dict[args.weights_config].keys()].to_dict(orient="records")
                for e_id in event_ids
            ],
            [
                sys[sys.Event_ID == e_id][weights_dict[args.weights_config].keys()].to_dict(orient="records")
                for e_id in event_ids
            ],
        ):
            gold_out, sys_out = matcher.match(gold_list, sys_list)
            si_gold.extend(gold_out)
            si_sys.extend(sys_out)

        if len(si_gold) != len(si_sys):
            logger.error(
                f"The length of the gold data does not match the length of the sys data '{len(gold)}!={len(sys)}'"
            )
            exit()

        gold, sys = pd.DataFrame(si_gold).replace(
            {float("nan"): None, "NULL ": None, "NULL": None, "None": None}
        ), pd.DataFrame(si_sys).replace({float("nan"): None, "NULL ": None, "NULL": None, "None": None})

        gold.to_parquet(f"{output_dir}/gold_{args.impact_type}.parquet", engine="fastparquet")
        sys.to_parquet(f"{output_dir}/sys_{args.impact_type}.parquet", engine="fastparquet")

    elif args.event_level in ["l1"]:
        logger.info("Only including events in the gold file!")
        sys = sys[sys.Event_ID.isin(gold["Event_ID"].to_list())]

    logger.info(f"The following events exist in gold:\n{pformat(gold['Event_ID'].unique())}")

    if args.score in ("wikipedia", "artemis"):
        # get article from source
        if "Source" in sys.columns:
            source_col_sys = "Source"
        elif "URL" in sys.columns:
            source_col_sys = "URL"
        else:
            logger.info("No source column found to determine article source... exiting.")
            exit()

        sys["Article_From"] = sys[source_col_sys].apply(lambda x: "artemis" if "artemis" in x else "wikipedia")
        assert sys["Article_From"][sys["Article_From"].isna()].shape == (
            0,
        ), f"Some article sources were not possible to determine by URL in the passed sys file, {sys['Article_From'][sys['Article_From'].isna()]}"

        gold["Article_From"] = gold[source_col_sys].apply(lambda x: "artemis" if "artemis" in x else "wikipedia")
        assert gold["Article_From"][gold["Article_From"].isna()].shape == (
            0,
        ), f"Some article sources were not possible to determine by URL in the passed gold file, {gold['Article_From'][gold['Article_From'].isna()]}"

        sys = sys[sys["Article_From"] == args.score]
        gold = gold[gold["Article_From"] == args.score]

        logger.info(f"Evaluation limited to {sys.shape} events from source {args.score}")

    if args.event_level == "l1":
        # Add dummy rows for missing events (for l1 event evaluation only)
        missing_ids = set(sys["Event_ID"].to_list()) ^ set(gold["Event_ID"].to_list())
        if missing_ids:
            logger.info(
                f"Missing events! {missing_ids}. The columns in these events will be constructed with `NoneType` objects. The system output will be penalized for missing events with the selected null penalty ({args.null_penalty})"
            )
            gold_cols = list(gold.columns)
            rows_to_add = []
            for event_id in missing_ids:
                # Create a dictionary for the new row with all columns set to "" except Administrative_AreaNorm which excepts a list
                new_row = {col: None for col in gold_cols}
                for col in any_area_columns:
                    if col in gold_cols:
                        new_row[col] = "[]"
                new_row["Event_ID"] = event_id  # Set the 'Event_ID'
                rows_to_add.append(new_row)

            missing_rows = pd.DataFrame(rows_to_add)
            sys = pd.concat([sys, missing_rows], ignore_index=True).sort_values("Event_ID")
            sys.replace({float("nan"): None}, inplace=True)

    # Align Monetary Categories by currency unit
    logger.info("Checking for monetary categories that need alignment.")
    monetary_categories = []
    if args.event_level == "l1":
        monetary_categories = ["Insured_Damage", "Damage"]
    elif "Damage".lower() in args.impact_type.lower() and args.event_level in [
        "l2",
        "l3",
    ]:
        if "Insured" in args.impact_type:
            monetary_categories = ["Insured_Damage"]
        elif "Damage" in args.impact_type and not "Insured" in args.impact_type and not "Buildings" in args.impact_type:
            monetary_categories = ["Damage"]

    for mc in monetary_categories:
        logger.info(f"Aligning monetary columns for category {mc}")
        if args.event_level == "l1":
            unit_col, adjusted_col, year_col, min_col, max_col = (
                f"Total_{mc}_Unit",
                f"Total_{mc}_Inflation_Adjusted",
                f"Total_{mc}_Inflation_Adjusted_Year",
                f"Total_{mc}_Min",
                f"Total_{mc}_Max",
            )
        else:
            unit_col, adjusted_col, year_col, min_col, max_col = (
                "Num_Unit",
                "Num_Inflation_Adjusted",
                "Num_Inflation_Adjusted_Year",
                "Num_Min",
                "Num_Max",
            )
        currency = CurrencyMatcher()
        sys_unit_col, aliged_col = (
            f"sys_unit_col_{mc}",
            f"aligned_{mc}",
        )
        gold[sys_unit_col] = sys[unit_col].to_numpy()
        gold[aliged_col] = gold.apply(
            lambda row: (
                currency.get_best_currency_match(row[sys_unit_col], row[unit_col])
                if row[unit_col] and row[sys_unit_col]
                else -1
            ),
            axis=1,
        )
        for col in [unit_col, adjusted_col, year_col, min_col, max_col]:
            gold[col] = gold.apply(
                lambda row: (row[col][row[aliged_col]] if row[aliged_col] >= 0 and row[col] is not None else None),
                axis=1,
            )

        gold.drop(columns=[sys_unit_col, aliged_col], inplace=True)

    # Specify null penalty
    null_penalty = args.null_penalty

    # Specify item weights
    _weights = weights_dict[args.weights_config]
    weights = {}
    for k, v in _weights.items():
        if k in gold.columns:
            weights[k] = v
        else:
            logger.info(f"Ignoring column {k} since it's not found in the gold file columns: {gold.columns}")

    logger.info(f"Chosen weights:\n {pformat(weights)}")

    # Instantiate comparer
    comp = Comparer(null_penalty, target_columns=weights.keys())
    logger.info(f"Target columns: {comp.target_columns}")

    if args.event_level == "l1":
        # sort by "Event_ID" only for main event evaluation
        sys = sys.sort_values("Event_ID")
        gold = gold.sort_values("Event_ID")

    list_type_cols = [x for x in any_area_columns if "Areas_" in x or "Locations_" in x]
    for col in list_type_cols:
        if col in sys.columns:
            sys[col] = sys[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        if col in gold.columns:
            gold[col] = gold[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    logger.info("Parsed strings to lists or dicts")

    sys_data = sys[weights.keys()].to_dict(orient="records")
    gold_data = gold[weights.keys()].to_dict(orient="records")

    if args.event_level == "l1" and monetary_categories:
        logger.info("Storing gold and sys files with matched currencies")
        gold[weights.keys()].to_parquet(
            f"{output_dir}/gold_matched_currencies_{args.event_level}.parquet", engine="fastparquet"
        )
        sys[weights.keys()].to_parquet(
            f"{output_dir}/sys_matched_currencies_{args.event_level}.parquet", engine="fastparquet"
        )
    pairs = zip(sys_data, gold_data)

    logger.info(f"Prepared {len(sys_data)} events for evaluation")

    comps = [
        [
            sys["Event_ID"],
            gold["Event_ID"],
            comp.weighted(sys, gold, weights),
            comp.all(sys, gold),
        ]
        for (sys, gold) in pairs
    ]
    all_comps = pd.DataFrame(
        [[i, j, c, d] + list(a.values()) for [i, j, (c, d), a] in comps],
        columns=["Event_ID1", "Event_ID2", "Coverage", "Weighted_Score"] + list(weights.keys()),
    ).replace({float("nan"): None})

    all_comps.sort_values("Weighted_Score")
    if args.event_level == "l1":
        all_comps.to_csv(
            f"{output_dir}/{args.event_level}_{args.score}_{len(sys_data)}_results.csv",
            index=False,
        )
    elif args.event_level in ["l2", "l3"]:
        all_comps.to_csv(
            f"{output_dir}/{args.event_level}_{args.score}_{len(sys_data)}_{args.impact_type}_results.csv",
            index=False,
        )
    averages = {}
    for i in all_comps.columns:
        if not i.startswith("Event_ID"):
            averages[i] = all_comps.loc[:, i].mean()

    if args.event_level == "l1":
        avg_result_filename = f"{output_dir}/{args.event_level}_{args.score}_{len(sys_data)}_avg_results.json"
    elif args.event_level in ["l2", "l3"]:
        avg_result_filename = (
            f"{output_dir}/{args.event_level}_{args.score}_{len(sys_data)}_{args.impact_type}_avg_results.json"
        )

    with open(avg_result_filename, "w") as f:
        json.dump(averages, f, indent=3)

    # get average per event_ID when evaluating specific instances
    if args.event_level in ["l2", "l3"]:
        all_comps["Event_ID"] = all_comps["Event_ID1"].apply(lambda x: x.split("-")[0])
        all_comps.groupby("Event_ID")[[c for c in all_comps.columns if not c.startswith("Event_ID")]].mean().to_csv(
            f"{output_dir}/{args.event_level}_{args.score}_{len(sys_data)}_{args.impact_type}_avg_per_event_id_results.csv",
            index=False,
        )

    logger.info(f"Done! Results in {avg_result_filename}")
