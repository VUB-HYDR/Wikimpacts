import argparse
import ast
import json

import comparer
import numpy as np
import pandas as pd

if __name__ == "__main__":
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

    args = parser.parse_args()

    gold = pd.read_parquet(args.gold_set_filepath, engine="pyarrow").replace(
        {np.nan: None, "NULL ": None, "NULL": None}
    )
    sys = pd.read_parquet(args.sys_set_filepath, engine="pyarrow").replace({np.nan: None, "NULL ": None, "NULL": None})

    print("Only including events in the gold file")
    sys = sys[sys.Event_ID.isin(gold["Event_ID"].to_list())]

    print(sys.shape, gold.shape)
    print(sys.columns)

    if args.score in ("wikipedia", "artemis"):
        # get article from source
        if "Source" in sys.columns:
            source_col_sys = "Source"
        elif "URL" in sys.columns:
            source_col_sys = "URL"
        else:
            print("No source column found... exiting.")
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

        print(f"Evaluation limited to {sys.shape} events from source {args.score}")
    assert len(sys.sort_values("Event_ID")["Event_ID"].to_list()) == len(
        gold.sort_values("Event_ID")["Event_ID"].to_list()
    ), f"Missing events! {set(sys.sort_values('Event_ID')['Event_ID'].to_list()) ^ set(gold.sort_values('Event_ID')['Event_ID'].to_list())}"

    # Specify null penalty
    null_penalty = args.null_penalty

    # Specify item weights
    weights = {
        "Event_ID": 1,
        "Main_Event": 1,
        "Event_Name": 0,
        "Total_Deaths_Min": 1,
        "Total_Deaths_Max": 1,
        "Total_Damage_Min": 1,
        "Total_Damage_Max": 1,
        "Total_Damage_Units": 1,
        "Start_Date_Day": 1,
        "Start_Date_Month": 1,
        "Start_Date_Year": 1,
        "End_Date_Day": 1,
        "End_Date_Month": 1,
        "End_Date_Year": 1,
        "Country_Norm": 1,
    }

    # Instantiate comparer
    comp = comparer.Comparer(null_penalty, target_columns=list(weights.keys()))
    print("Target columns", comp.target_columns)

    sys = sys.sort_values("Event_ID")
    gold = gold.sort_values("Event_ID")

    for col in ["Country_Norm"]:
        sys[col] = sys[col].apply(ast.literal_eval)
        gold[col] = gold[col].apply(ast.literal_eval)

    print("Parsed strings to lists or dicts")

    sys_data = sys[list(weights.keys())].to_dict(orient="records")
    gold_data = gold[list(weights.keys())].to_dict(orient="records")

    pairs = zip(sys_data, gold_data)
    print(f"Prepared {len(sys_data)} events for evaluation")

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
        f"Database/evaluation_results/{args.model_name}_{args.score}_{len(sys_data)}_results.csv", index=False
    )

    averages = {}
    for i in all_comps.columns:
        if not i.startswith("Event_ID"):
            averages[i] = all_comps.loc[:, i].mean()

    avg_result_filename = f"Database/evaluation_results/{args.model_name}_{args.score}_{len(sys_data)}_avg_results.json"
    with open(avg_result_filename, "w") as f:
        json.dump(averages, f)

    print(f"Done! Results in {avg_result_filename}")
