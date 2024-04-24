# Wikimpacts
Wikimapcts is the first version of climate impact dataset creating by generative AI GPT4.0


### Dependencies
Prerequisite:
- Install [`poetry`](https://python-poetry.org/docs/#installation)
Then activate a virtual environment and install the dependencies:

```shell
poetry shell # activates a venv
poetry install  # installs all dependencies from the lockfile
```

- [Create a Bing Maps Account](https://learn.microsoft.com/en-us/bingmaps/getting-started/bing-maps-dev-center-help/creating-a-bing-maps-account), then (generate an api key)[https://learn.microsoft.com/en-us/bingmaps/getting-started/bing-maps-dev-center-help/getting-a-bing-maps-key]. Place the key in a `.env` file:

```shell
BING_MAPS_API_KEY=my-long-api-key-fr    om-bing-maps
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


#### Sources & Citations
- GADM world data | `Database/data/gadm_world.csv`

    https://gadm.org/license.html

- Regions by UNSD | `Database/data/UNSD — Methodology.csv`

    United Nations Standard Country Code, Series M: Miscellaneous Statistical Papers, No. 49, New York: United Nations. ST/ESA/STAT/SER.M/49
    https://unstats.un.org/unsd/classifications/Family/Detail/12