# Wikimpacts
Wikimapcts is the first version of climate impact dataset creating by generative AI GPT4.0


## Dependencies
Prerequisite:
- Install [`poetry`](https://python-poetry.org/docs/#installation)
Then activate a virtual environment and install the dependencies:

```shell
poetry shell # activates a venv
poetry install # installs all dependencies from the lockfile
```

- Install pre-commit

```shell
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

- Install [Git Large File Storage](https://git-lfs.com/) to enable pushing large files to the repository

```
# install after downloading from https://git-lfs.com
git lfs install
```

## Quickstart

### Run prompt experiments on OpenAI models
If you use OpenAI models, there is a way to save your cost with running experiments in batch.
#### (Step 1) Raw output
Choose the raw file contains the text you need to process, please use the clear raw file name to indicate your experiment, this name will be used as the output file, the api env you want to use, the decription of the experiment, the prompt category, and the batch file location you want to store the batch file (this is not mandatory, but it's good to check if you create correct batch file)

#### (Step 2) GPT models
Choose the model you want to apply. The default model is "gpt-4o-2024-05-13"
- below is a command example you can refer to run the script:
```shell
poetry run python3 Database/Prompts/run_prompts.py --filename wiki_dev_whole_infobox_20240729_70single_events.json --raw_dir Database/Wiki_dev_test_articles  --batch_dir  Database/Prompts/batch  --api_env .env  --description all_categories_V3  --prompt_category impact
```
#### (Step 3) Retrieve results
Choose the same raw file as you run the experiment, the same api env to access your remote OpenAI server and the output directory to store your result.
- below is a command example you can refer to run the script:
```shell
poetry run python3  Database/Prompts/batch_output_retrivel.py  --api_env .env  --output_dir  Database/raw/batch_test  --file_name wiki_dev_whole_infobox_20240729_70single_events.json  --raw_dir  Database/Wiki_dev_test_articles --description all_categories_V3
```
### Parsing and evaluation pipeline

If you have generated some LLM output and would like to test it against the dev and test gold sets, here is a list of command to enable you to experiment with this yourself.

#### (Step 1) Experiment name

Choose a new experiment name! You will use this <EXPERIMENT_NAME> for the whole pipeline.

#### PRESTEP (before Step 2):
If the system output is split across several files (such as Mixtral and Mistral system outputs), then first merge it:

- Normalizing JSON output for Mistral/Mixtral
    If the system output is split across several files (such as Mixtral and Mistral system outputs), then first merge it:

    ```shell
    poetry run python3 Database/merge_json_output.py \
    --input_dir Database/raw/<EXPERIMENT_NAME>/<RAW_JSON_FILES> \
    --output_dir Database/raw/<EXPERIMENT_NAME> \
    --model_name <MY_MODEL>
    ```

- Normalizing JSON output for GPT4o

    GPT4o sometimes produces inconsistent JSON where it nests keys like "Location" under "Location_Information" and start and end date under the key "Time_Information". In this case, you need to unnest these using the script below:


    ```shell
    poetry run python3 Database/fix_nested_json.py \
    -i "Database/raw/<EXPERIMENT_NAME>/<INPUT_FILE.JSON>" \
    -o "Database/raw/<EXPERIMENT_NAME>/<OUTPUT_FILE.JSON>"
    ```

> [!WARNING]
> Your raw system output files should always land in the `Database/raw/<EXPERIMENT_NAME>` directory!

> [!TIP]
>  JSON files can be formatted easily with pre-commit:
>
> ```shell
> pre-commit run --files Database/raw/<EXPERIMENT_NAME>/> <JSON_FILE_THAT_NEEDS_FORMATTING>
> ```

#### (Step 2) Parsing events and subevents

Once all system output files are merged into a single JSON file (**or if this was already the case, such as with GPT4 output**), you can parse them so they are ready to be evaluated.
    The parsing script [`Database/parse_events.py`](Database/parse_events.py) will normalize numbers (to min and max) and locations (using OpenStreetMap) and output a JSON file.

```shell
poetry run python3 Database/parse_events.py \
--raw_dir Database/raw/<EXPERIMENT_NAME> \
--filename <JSON_FILE> \
--output_dir Database/output/<EXPERIMENT_NAME> \

# "sub", "main" or "all"
--event_type all \

# if your country and location columns have a different name
# you can specify it here (otherwise, defaults to
# "Country" and "Location" (respectively)):
--country_column "Custom_Country_Column"  \
--location_column "Locations"
```

> [!WARNING]
> Normalizing countries will go slow the first time. This is because we are using a free API (currently!). However, each time this script is run locally, geopy will cache the results, meaning that it will go faster the next time you run it on your local branch. Allow for 15-20 minutes the first time.


#### (Step 2) Evaluate against the dev and test sets

##### (A) Choose your config and columns
The python dictionary in <a href="Evaluation/weights.py"><code>weights.py</code></a> contains different weight configs. For example, the experiments nlp4climate weighs all the column types equally but excludes the "Event_Name" from evaluation.

Also, this config will result in evaluating only on this smaller set of columns, so this list also functions as a set of columns that will be included in the evaluation script for this experiment.

> [!NOTE]
> If any of these columns are not found in your gold file, they will be ignored

```python
    "weights" = {
        "nlp4climate": {
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

        },
    }
```


##### (B) Evaluate main events
 When your config is ready, run the evaluation script:

```shell
poetry run python3 Evaluation/evaluator.py --sys-file  Database/output/<EXPERIMENT_NAME>/dev/<EXPERIMENT.PARQUET> --gold-file Database/gold/<EXPERIMENT_GOLD.PARQUET> --model-name "<EXPERIMENT_NAME>/<DATA_SPLIT>" --null-penalty 1 --score all --weights_config <EXPERIMENT_NAME>
```

For example, the script below runs the evaluation on the output from mixtral-8x7b-insctruct agains the dev set gold file, and saves the results in `Database/evaluation_results/example/dev`:

```shell
poetry run python3 Evaluation/evaluator.py --sys-file  Database/output/nlp4climate/dev/mixtral-8x7b-instruct-source.parquet \
--gold-file Database/gold/gold_dev_20240515.parquet \
--model-name "example/dev" \
--null-penalty 1 \
--score all \
--weights_config nlp4climate
```

#### Evaluate sub events (ie. specific instances)

Specific instances can be evaluated using the same script. The same script (`Evaluation/evalutor.py`) will automatically match specific instances from the gold data with the system output. If no match exists for a specific instance, it will be matched up with a "padded" example with NULL values so that the system is penalized for not having been able to find a particular specific instance or for finding extra specific instances not found in the gold dataset.

Below is a scipt that evaluates two dummy sets (gold and sys) to showcase a working example and the correct schema for the `.parquet` files. Sub events are evaluated separately from main events.

```shell
poetry run python3 Evaluation/evaluator.py \
--sys-file tests/specific_instance_eval/test_sys_list_death.parquet \
--gold-file tests/specific_instance_eval/test_gold_list_death.parquet \
--model-name "specific_instance_eval_test/dev/deaths" \
--event_type sub \
--weights_config specific_instance \
--specific_instance_type deaths
```
If run properly, you should see the results in `Database/evaluation_results/specific_instance_eval_test`:

```shell
Database/evaluation_results/specific_instance_eval_test
└── dev
    └── deaths
        ├── all_27_deaths_avg_per_event_id_results.csv # <- average error rate grouped by event_id
        ├── all_27_deaths_avg_results.json # <- overall average results
        ├── all_27_deaths_results.csv # <- results for each pair of gold/sys
        ├── gold_deaths.parquet # <- modified gold file with matches + padded specific instances
        └── sys_deaths.parquet # <- modified sys file with matches + padded specific instances
```

> [!WARNING]
> Do not commit these files to your branch or to `main`, big thanks!

### Parsing and normalization

If you have new events to add to the database, first parse them and insert them.

- To parse events (and normalize their values) from a json file with the right schema (adding schema validation soon), run:

    ```shell
    # an example
    poetry run python3 Database/parse_events.py --spaCy_model "en_core_web_trf" --filename "some_json_file.json" --raw_path "Database/raw" --locale "en_US.UTF-8"

    # for help
    poetry run python3 Database/parse_events.py --help
    ```

### Inserting
- To insert new main events:

    ```shell
    # to append
    poetry run python3 Database/insert_main_event.py -m "append"

    # to replace
    poetry run python3 Database/insert_main_event.py -m "replace"

    # explore more options
    poetry run python3 Database/parse_events.py --help
    ```

- To insert new subevents:

    ```shell
    poetry run python3 Database/insert_sub_events.py [options]

    # see options
    poetry run python3 Database/parse_events.py --help
    ```

### Database-related
- To generate the database according to [`Database/schema.sql`](Database/schema.sql):

    ```shell
    poetry run python3 Database/create_db.py
    ```

#### SPECIAL USECASE: Converting the manual annotation table from a flat format to Events and Specific Impacts

1. Download the latest copy of the excel sheet (write one of the contributors of the repository if you do not have the link)
2. Choose the correct excel sheet and run the script:

```shell
# Change DDMMYYY to the datestamp of the excel sheet to parse
poetry run python3 Database/gold_from_excel.py --input-file "Database/gold/ImpactDB_DataTable_Validation.xlsx" \
--sheet-name ImpactDB_manual_copy_MDMMYYY  \
--output-dir Database/gold/gold_from_excel
```

These results are not split to test/dev.

> [!IMPORTANT]
> Please don't track or push excel sheets into the repository
> The file `Database/gold/ImpactDB_DataTable_Validation.xlsx` has the latest gold annotations from 01/06/2024 and will be updated in the future.

### Develop

Always pull a fresh copy of the `main` branch first! To add a new feature, check out a new branch from the `main` branch, make changes there, and push the new branch upstream to open a PR. PRs should result in a **squash commit** in the `main` branch. **It is recommended to code responsibly and ask someone to review your code. You can always tag [i-be-snek](https://github.com/i-be-snek) as a reviewer.**

Always _**rebase**_ your branch on the latest changes in `main` instead of merging using `git rebase main`. If you are having trouble with resolving merge conflicts when rebasing, consult [i-be-snek](https://github.com/i-be-snek).

And don't forget to pull large files from Git Large File Storage!

```
# always pull first
git pull main

# fetch and merge all files for your current branch
git lfs pull

# fetch and merge all files for ALL branches
git lfs pull --all
```

> [!TIP]
> Consult this [StackOverflow answer on how to use `git lfs`](https://stackoverflow.com/a/72610495/14123992)


Make sure any new dependencies are handled by `poetry`.You should be tracking and pushing both `poetry.lock` and `pyproject.toml` files.
There is no need to manually add dependencies to the `pyproject.toml` file. Instead, use `poetry` commands:

```shell
# add pandas as a main dependency
poetry add pandas -G main

# add a specific version of ipykernel as a dev dependency
poetry add ipykernel@6.29.4 -G dev
```

### Problems?

Start an Issue on GitHub if you find a bug in the code or have suggestions for a feature you need.
If you run into an error or problem, please include the error trace or logs! :D

> [!TIP]
> Consult this [Github Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

### Sources & Citations
- GADM world data | `Database/data/gadm_world.csv`

    https://gadm.org/license.html

- Regions by UNSD | `Database/data/UNSD — Methodology.csv`

    United Nations Standard Country Code, Series M: Miscellaneous Statistical Papers, No. 49, New York: United Nations. ST/ESA/STAT/SER.M/49
    https://unstats.un.org/unsd/classifications/Family/Detail/12
