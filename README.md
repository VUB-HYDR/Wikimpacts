# Wikimpacts
Wikimapcts is the first version of climate impact dataset creating by generative AI GPT4.0


### Dependencies
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

### Quickstart

#### Parsing and evaluation pipeline

If you have generated some LLM output and would like to test it against the dev and test gold sets, here is a list of command to enable you to experiment with this yourself.

1. Choose a new experiment name! You will use this <EXPERIMENT_NAME> for the whole pipeline.

**PRESTEP**:  
    If the system output is split across several files (such as Mixtral and Mistral system outputs), then first merge it:

    ```shell
        poetry run python3 Database/merge_json_output.py \
        --input_dir Database/raw/<EXPERIMENT_NAME>/<RAW_JSON_FILES> \
        --output_dir Database/raw/<EXPERIMENT_NAME> \
        --model_name <MY_MODEL>
    ```


> [!WARNING]  
> Your raw system output files should always land in the `Database/raw/<EXPERIMENT_NAME>` directory!

> [!TIP]
>  JSON files can be formatted easily with pre-commit:
> 
> ```shell
> pre-commit run --files Database/raw/<EXPERIMENT_NAME>/> <JSON_FILE_THAT_NEEDS_FORMATTING>
> ```

2. Once all system output files are merged into a single JSON file (**or if this was already the case, such as with GPT4 output**), you can parse them so they are ready to be evaluated. 
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


3. Evaluate against the dev and test sets 

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
 

##### (B) Evaluate
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

#### Parsing and normalization

If you have new events to add to the database, first parse them and insert them.

- To parse events (and normalize their values) from a json file with the right schema (adding schema validation soon), run:

    ```shell
    # an example
    poetry run python3 Database/parse_events.py --spaCy_model "en_core_web_trf" --filename "some_json_file.json" --raw_path "Database/raw" --locale "en_US.UTF-8"

    # for help
    poetry run python3 Database/parse_events.py --help
    ```

#### Inserting
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

#### Database-related
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
The plan is to expand this functionality further and evaluate subevents

To be implemented: 
- [ ] How to evaluate subevents when the gold may contain more/less than the system output? Maybe subevents can be matched by location and timestamp and evaluated accordingly -- finding too many could be penalized. 
- [ ] Match the short uuids (generated by [Database/scr/normalize_utils.pyrandom_short_uuid](Database/scr/normalize_utils.pyrandom_short_uuid)) in the excel sheet for the ones that already exist in the dev and test sets.
- [ ] Make any edits (if needed) to the evaluation script so it can handle subevents

(Input appreciated! Just email @i-be-snek)

> [!IMPORTANT]
> Please don't track or push excel sheets into the repository
> The file `Database/gold/ImpactDB_DataTable_Validation.xlsx` has the latest gold annotations from 01/06/2024 and will be updated in the future. 

#### Develop

Always pull a fresh copy of the `main` branch first! To add a new feature, check out a new branch from the `main` branch, make changes there, and push the new branch upstream to open a PR. PRs should result in a **squash commit** in the `main` branch. It is recommended to code responsibly and ask someone to review your code. 

Make sure any new dependencies are handled by `poetry`.You should be tracking and pushing both `poetry.lock` and `pyproject.toml` files. 
There is no need to manually add dependencies to the `pyproject.toml` file. Instead, use `poetry` commands:

```shell
# add pandas as a main dependency
poetry add pandas -G main 

# add a specific version of ipykernel as a dev dependency
poetry add ipykernel@6.29.4 -G dev
```

#### Problems?

Start an Issue on GitHub if you find a bug in the code or have suggestions for a feature you need. 
If you run into an error or problem, please include the error trace or logs! :D 

> [!TIP]
> Consult this [Github Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

#### Sources & Citations
- GADM world data | `Database/data/gadm_world.csv`

    https://gadm.org/license.html

- Regions by UNSD | `Database/data/UNSD — Methodology.csv`

    United Nations Standard Country Code, Series M: Miscellaneous Statistical Papers, No. 49, New York: United Nations. ST/ESA/STAT/SER.M/49
    https://unstats.un.org/unsd/classifications/Family/Detail/12
