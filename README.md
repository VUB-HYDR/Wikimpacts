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

If you have new events to add to the database, first parse them and insert them.

#### Parsing and normalization
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

#### Sources & Citations
- GADM world data | `Database/data/gadm_world.csv`

    https://gadm.org/license.html

- Regions by UNSD | `Database/data/UNSD — Methodology.csv`

    United Nations Standard Country Code, Series M: Miscellaneous Statistical Papers, No. 49, New York: United Nations. ST/ESA/STAT/SER.M/49
    https://unstats.un.org/unsd/classifications/Family/Detail/12
