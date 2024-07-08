import argparse
import ast
import json
from weights import weights as weights_dict
import comparer
import numpy as np
import pandas as pd
import pathlib
from pprint import pformat
from utils import Logging

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

    args = parser.parse_args()

    output_dir = f"Database/evaluation_results/{args.model_name}"
    logger.info(f"Creating {output_dir} if it does not exist!")
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True) 

    gold = pd.read_parquet(args.gold_set_filepath, engine="fastparquet").replace(
        {np.nan: None, "NULL ": None, "NULL": None}
    )
    sys = pd.read_parquet(args.sys_set_filepath, engine="fastparquet").replace({np.nan: None, "NULL ": None, "NULL": None})

    logger.info("Only including events in the gold file")
    sys = sys[sys.Event_ID.isin(gold["Event_ID"].to_list())]

    if args.score in ("wikipedia", "artemis"):
        # get article from source
        if "Source" in sys.columns:
            source_col_sys = "Source"
        elif "URL" in sys.columns:
            source_col_sys = "URL"
        else:
            logger.info("No source column found... exiting.")
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
    assert len(sys.sort_values("Event_ID")["Event_ID"].to_list()) == len(
        gold.sort_values("Event_ID")["Event_ID"].to_list()
    ), f"Missing events! {set(sys.sort_values('Event_ID')['Event_ID'].to_list()) ^ set(gold.sort_values('Event_ID')['Event_ID'].to_list())}"

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
    comp = comparer.Comparer(null_penalty, target_columns=weights.keys())
    logger.info(f"Target columns: {comp.target_columns}")

    for col in ["Country_Norm"]:
        sys[col] = sys[col].apply(ast.literal_eval)
        gold[col] = gold[col].apply(ast.literal_eval)

    logger.info("Parsed strings to lists or dicts")
    sys_data = sys.to_dict(orient="records")
    gold_data = gold.to_dict(orient="records")

    pairs = zip(sys_data, gold_data)
    logger.info(f"Prepared {len(sys_data)} events for evaluation")

    comps = [
        [sys["Event_ID"], gold["Event_ID"], comp.weighted(sys, gold, weights), comp.all(sys, gold)]
        for (sys, gold) in pairs
    ]
    all_comps = pd.DataFrame(
        [[i, j, c, d] + list(a.values()) for [i, j, (c, d), a] in comps],
        columns=["Event_ID1", "Event_ID2", "Coverage", "Weighted_Score"] + list(weights.keys()),
    ).replace({np.nan: None})

    all_comps.sort_values("Weighted_Score")
    all_comps.to_csv(
        f"{output_dir}/{args.score}_{len(sys_data)}_results.csv", index=False
    )

    averages = {}
    for i in all_comps.columns:
        if not i.startswith("Event_ID"):
            averages[i] = all_comps.loc[:, i].mean()


    avg_result_filename = f"{output_dir}/{args.score}_{len(sys_data)}_avg_results.json"
    with open(avg_result_filename, "w") as f:
        json.dump(averages, f)

    logger.info(f"Done! Results in {avg_result_filename}")
