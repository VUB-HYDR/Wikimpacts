import argparse
import ast
import json
import pathlib
from pprint import pformat, pprint

import numpy as np
import pandas as pd

from Evaluation.comparer import Comparer
from Evaluation.matcher import SpecificInstanceMatcher
from Evaluation.utils import Logging
from Evaluation.weights import weights as weights_dict

if __name__ == "__main__":
    logger = Logging.get_logger("evaluator")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-sys",
        "--sys-file",
        dest="sys_set_filepath",
        help="The full path to the system output in parquet",
        type=str,
    )

    parser.add_argument(
        "-gold",
        "--gold-file",
        dest="gold_set_filepath",
        help="The full path to the gold set in parquet",
        type=str,
    )

    parser.add_argument(
        "-m",
        "--model-name",
        dest="model_name",
        help="A model name to store the results",
        type=str,
    )

    parser.add_argument(
        "-null",
        "--null-penalty",
        dest="null_penalty",
        default=1,
        help="Null penalty, defaults to 1",
        type=int,
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
        "-t",
        "--event_type",
        dest="event_type",
        default="main",
        choices=["main", "sub"],
        help="Choose which events to parse. Possible values: main or sub",
        type=str,
    )

    parser.add_argument(
        "-si",
        "--specific_instance_type",
        dest="specific_instance_type",
        default="specific_instance",
        help="""Supply the specific instance type/category (example: 'deaths', 'insurance_damage')
            to store matched specific instances for gold and sys""",
        type=str,
        required=False,
    )

    args = parser.parse_args()

    output_dir = f"Database/evaluation_results/{args.model_name}"
    logger.info(f"Creating {output_dir} if it does not exist!")
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

    matcher = SpecificInstanceMatcher()

    gold = pd.read_parquet(args.gold_set_filepath, engine="fastparquet").replace(
        {np.nan: None, "NULL ": None, "NULL": None}
    )

    sys = pd.read_parquet(args.sys_set_filepath, engine="fastparquet").replace(
        {np.nan: None, "NULL ": None, "NULL": None}
    )

    if args.event_type == "sub":
        logger.info("Pairing up specific instances ('sub-events')")
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

        gold, sys = pd.DataFrame(si_gold).replace({np.nan: None, "NULL ": None, "NULL": None}), pd.DataFrame(
            si_sys
        ).replace({np.nan: None, "NULL ": None, "NULL": None})

        gold.to_parquet(f"{output_dir}/gold_{args.specific_instance_type}.parquet")
        sys.to_parquet(f"{output_dir}/sys_{args.specific_instance_type}.parquet")

    if args.event_type == "main":
        logger.info("Only including events in the gold file!")
        sys = sys[sys.Event_ID.isin(gold["Event_ID"].to_list())]

    logger.info(f"The following events exist in gold: {pprint(list(gold['Event_ID'].unique()), indent=10)}")

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

    if args.event_type == "main":
        # Add dummy rows for missing events (for main event evaluation only)
        missing_ids = set(sys["Event_ID"].to_list()) ^ set(gold["Event_ID"].to_list())
        if missing_ids:
            logger.info(
                f"Missing events! {missing_ids}. The columns in these events will be constructed with `NoneType` objects. The system output will be penalized for missing events with the selected null penalty ({args.null_penalty})"
            )
            gold_cols = list(gold.columns)
            rows_to_add = []
            for event_id in missing_ids:
                # Create a dictionary for the new row with all columns set to "" except Country_Norm which excepts a list
                new_row = {col: None for col in gold_cols}
                for col in ["Country_Norm", "Location_Norm"]:
                    if col in gold_cols:
                        new_row[col] = "[]"
                new_row["Event_ID"] = event_id  # Set the 'Event_ID'
                rows_to_add.append(new_row)

            missing_rows = pd.DataFrame(rows_to_add)
            sys = pd.concat([sys, missing_rows], ignore_index=True).sort_values("Event_ID")
            sys.replace({np.nan: None}, inplace=True)

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

    if args.event_type == "main":
        # sort by "Event_ID" only for main event evaluation
        sys = sys.sort_values("Event_ID")
        gold = gold.sort_values("Event_ID")

    list_type_cols = ["Country_Norm", "Location_Norm"] if args.event_type == "main" else ["Location_Norm"]
    for col in list_type_cols:
        if col in sys.columns:
            sys[col] = sys[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        if col in gold.columns:
            gold[col] = gold[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    logger.info("Parsed strings to lists or dicts")

    sys_data = sys[weights.keys()].to_dict(orient="records")
    gold_data = gold[weights.keys()].to_dict(orient="records")

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
    ).replace({np.nan: None})

    all_comps.sort_values("Weighted_Score")
    if args.event_type == "main":
        all_comps.to_csv(f"{output_dir}/{args.score}_{len(sys_data)}_results.csv", index=False)
    elif args.event_type == "sub":
        all_comps.to_csv(
            f"{output_dir}/{args.score}_{len(sys_data)}_{args.specific_instance_type}_results.csv", index=False
        )
    averages = {}
    for i in all_comps.columns:
        if not i.startswith("Event_ID"):
            averages[i] = all_comps.loc[:, i].mean()

    if args.event_type == "main":
        avg_result_filename = f"{output_dir}/{args.score}_{len(sys_data)}_avg_results.json"
    elif args.event_type == "sub":
        avg_result_filename = (
            f"{output_dir}/{args.score}_{len(sys_data)}_{args.specific_instance_type}_avg_results.json"
        )

    with open(avg_result_filename, "w") as f:
        json.dump(averages, f)

    logger.info(f"Done! Results in {avg_result_filename}")
