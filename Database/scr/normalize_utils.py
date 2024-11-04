import ast
import json
import os
import pathlib
import re
from datetime import datetime
from typing import Tuple, Union

import pandas as pd
import pycountry
import shortuuid
from dateparser.date import DateDataParser
from dateparser.search import search_dates
from iso4217 import Currency
from spacy import language as spacy_language
from unidecode import unidecode

from .log_utils import Logging
from .normalize_numbers import NormalizeNumber


class NormalizeUtils:
    def __init__(self):
        self.logger = Logging.get_logger("normalize-utils")

    def load_spacy_model(self, spacy_model: str = "en_core_web_trf") -> spacy_language:
        import spacy

        try:
            nlp = spacy.load(spacy_model, enable=["transformer", "ner", "tagger"])
            self.logger.info(f"SpaCy model '{spacy_model}' has been loaded")

        except OSError:
            self.logger.info(
                f"SpaCy model '{spacy_model}' is not downloaded. Dowloading now - this might take a minute"
            )
            from spacy.cli import download

            download(spacy_model)
            nlp = spacy.load(spacy_model)
        return nlp

    @staticmethod
    def random_short_uuid(length: int = 7) -> str:
        """Generates a short alpha-numerical UID"""
        return shortuuid.ShortUUID().random(length=length)

    @staticmethod
    def replace_nulls(df: pd.DataFrame) -> pd.DataFrame:
        """Normalizes all variations of NULL, NaN, nan, null either as data types or as strings"""
        any_NULL = re.compile(r"^\s*(null)\s*$|^\s*(nan)\s*$", re.IGNORECASE | re.MULTILINE)
        df = df.replace(any_NULL, None, regex=True)
        df = df.astype(object).where(pd.notnull(df), None)
        return df

    def normalize_date(self, row: Union[str, None]) -> Tuple[int, int, int]:
        """
        See https://github.com/scrapinghub/dateparser/issues/700
        and https://dateparser.readthedocs.io/en/latest/dateparser.html#dateparser.date.DateDataParser.get_date_data

        Returns a tuple: (day, month, year) with None for missing values
        """
        if not row:
            return (None, None, None)

        if row is not None:
            ddp = DateDataParser(
                settings={
                    "REQUIRE_PARTS": ["year"],
                    "NORMALIZE": True,
                    "PREFER_DATES_FROM": "past",
                }
            )

            year, month, day = "%Y", "%m", "%d"

            try:
                date = ddp.get_date_data(row)
                try:
                    date.date_obj.strftime("%Y-%m-%d")
                except:
                    return (None, None, None)

                if date.period == "year":
                    return (None, None, date.date_obj.strftime(year))

                elif date.period == "month":
                    return (
                        None,
                        date.date_obj.strftime(month),
                        date.date_obj.strftime(year),
                    )

                elif date.period == "day":
                    return (
                        date.date_obj.strftime(day),
                        date.date_obj.strftime(month),
                        date.date_obj.strftime(year),
                    )

            except BaseException as err:
                self.logger.error(f"Date parsing error in {row} with date\n{err}\n")
                return (None, None, None)

    @staticmethod
    def unpack_col(df: pd.DataFrame, columns: list = []) -> pd.DataFrame:
        """Unpacks Total_Summary_* columns"""
        for c in columns:
            json_normalized_df = pd.json_normalize(df[c])
            cat = c.split("Total_Summary_")[1]
            bad_columns = [x for x in json_normalized_df.columns if not x.startswith(f"Total_{cat}")]
            for bad_col_name in bad_columns:
                fix_col_name = f"Total_{cat}_{bad_col_name}"
                json_normalized_df.rename(columns={bad_col_name: fix_col_name}, inplace=True)

            df = pd.concat([json_normalized_df, df], axis=1)
            df.drop(columns=[c], inplace=True)
        return df

    def eval(self, x: list | str):
        try:
            if isinstance(x, str):
                if x[0] == "[" or x[0] == "{":
                    return ast.literal_eval(x)
                else:
                    return x
            elif isinstance(x, list) or isinstance(x, dict) or x == None or x == float("nan"):
                return x
            else:
                raise BaseException
        except BaseException as err:
            self.logger.debug(
                f"Literal Eval Error for {x} of type {type(x)}.\nError trace: {err}. Returning {None} of type {type(None)}"
            )
            return None

    @staticmethod
    def filter_null_list(lst: list) -> list:
        new_list = []
        for l in lst:
            if isinstance(l, str):
                if l.lower().strip() not in ["null", "none"]:
                    new_list.append(l)
            elif l == float("nan") or l is None:
                pass
            else:
                new_list.append(l)
        return new_list

    @staticmethod
    def filter_null_str(l: str | None) -> str | None:
        if isinstance(l, str):
            if l.lower().strip() in ["null", "none"]:
                return None
        if l == float("nan") or l is None:
            return None
        return l

    @staticmethod
    def simple_country_check(c: str):
        try:
            exists = pycountry.countries.search_fuzzy(c)[0].official_name
        except:
            try:
                exists = pycountry.countries.search_fuzzy(c)[0].name
            except:
                try:
                    exists = pycountry.historic_countries.search_fuzzy(c)[0].name
                except:
                    # TODO: fuzzy-match from GADM
                    return False
        return True if exists else False

    @staticmethod
    def df_to_parquet(
        df: pd.DataFrame,
        target_dir: str,
        chunk_size: int = 2000,
        **parquet_wargs,
    ):
        """Writes pandas DataFrame to parquet format with pyarrow.
            Credit: https://stackoverflow.com/a/72010262/14123992
        Args:
            df: DataFrame
            target_dir: local directory where parquet files are written to
            chunk_size: number of rows stored in one chunk of parquet file. Defaults to 2000.
        """
        pathlib.Path(target_dir).mkdir(parents=True, exist_ok=True)
        existing_chunks = os.listdir(target_dir)
        begin_at = 0
        if existing_chunks:
            begin_at = int(sorted(existing_chunks)[-1].split(".")[0]) + 1
        for i in range(0, len(df), chunk_size):
            slc = df.iloc[i : i + chunk_size]
            chunk = int(i / chunk_size) + begin_at
            fname = os.path.join(target_dir, f"{chunk:04d}.parquet")
            slc.to_parquet(fname, engine="fastparquet", **parquet_wargs)

    @staticmethod
    def df_to_json(
        df: pd.DataFrame,
        target_dir: str,
        chunk_size: int = 2000,
        **json_wargs,
    ):
        """Writes pandas DataFrame to json format
            Credit: https://stackoverflow.com/a/72010262/14123992
        Args:
            df: DataFrame
            target_dir: local directory where parquet files are written to
            chunk_size: number of rows stored in one chunk of parquet file. Defaults to 2000.
        """
        for i in range(0, len(df), chunk_size):
            slc = df.iloc[i : i + chunk_size]
            chunk = int(i / chunk_size)
            fname = os.path.join(target_dir, f"{chunk:04d}.json")
            pathlib.Path(target_dir).mkdir(parents=True, exist_ok=True)
            slc.to_json(fname, **json_wargs)

    def check_currency(self, currency_text: str) -> bool:
        try:
            Currency(currency_text)
            return True
        except ValueError as err:
            self.logger.error(f"Bad currency found: `{currency_text}`: {err}")
            return False

    def check_date(self, year: int, month: int, day: int) -> bool:
        try:
            datetime(year, month, day)
            return True
        except ValueError as err:
            self.logger.error(f"Y: {year}; M: {month}; D: {day}. Error: {err}")
            return False


class NormalizeJsonOutput:
    def __init__(self):
        self.logger = Logging.get_logger("normalize-utils-json")

    @staticmethod
    def infer_date_from_dict(x: any) -> str:
        """
        This function normalizes date output in various formats by some LLMs.
        Current usecases:
            - Mixtral and Mistral models since they may produce date output that is inconsistent
            - [Add more here]
        More cases can be added if necessary.

        If the passed "date" object is a dictionary with keys "time", "date", or "year", "month", and "day"
        (eg {"day": 1, "month": 5, "year": 2025} or {"date": "2012-12-21"}),the function extracts the date and reconstructs it,
        returning it as a string. If none of those keys are present, the function searches the values of each key for a full date to extract.

        If no date is found, an empty string is returned.
        """
        if isinstance(x, str):
            return x
        if isinstance(x, list):
            return x[0]
        elif isinstance(x, dict):
            normalized_x = {}
            for k, v in x.items():
                normalized_x[k.strip().lower()] = str(v)
            day, month, year, date, time = None, None, None, None, None
            if "year" in normalized_x.keys():
                if "year" in normalized_x.keys():
                    year = normalized_x["year"]
                if "month" in normalized_x.keys():
                    month = normalized_x["month"]

                if "day" in normalized_x.keys():
                    day = normalized_x["day"]

            elif "date" in normalized_x.keys():
                date = normalized_x["date"]
            elif "time" in normalized_x.keys():
                time = normalized_x["time"]
            else:
                for k in normalized_x.keys():
                    text = search_dates(
                        normalized_x[k],
                        settings={"STRICT_PARSING": False, "DATE_ORDER": "DMY"},
                    )
                    for x in text:
                        if x:
                            date_string = x[0]
                            date = date_string
                            break

        result = None
        if year and month and day:
            result = f"{day}-{month}-{year}"
        elif year and month:
            result = f"{month}-{year}"
        elif year:
            result = year
        elif time:
            result = time
        elif date:
            result = date  # prefer date if present
        return result if result is not None else ""

    def merge_json(self, file_path_dir: str) -> list[pd.DataFrame]:
        """
        Merges single events in JSON into one single JSON file (orientation: records).
        Assigns each file to the "Event_Name" column.
        Assumes a directory path containing json files where the file name corresponds to the "Event Name".
        """

        file_list = os.listdir(file_path_dir)
        file_list_relative = [f"{file_path_dir}/{i}" for i in file_list if i and i.endswith(".json")]

        dfs = []
        for idx in range(len(file_list_relative)):
            try:
                json_file = json.load(open(file_list_relative[idx]))
                country_col = None
                if json_file:
                    columns = list(json_file.keys())
                    country_col = [
                        i
                        for i in columns
                        if i.lower().strip().startswith("countr") and not i.lower().strip().endswith("annota")
                    ]

                    if len(country_col) >= 1:
                        country_col = country_col[0]
                    else:
                        country_col = None

                # normalize country columns
                if country_col:
                    try:
                        if len(json_file[country_col]) >= 1 and isinstance(json_file[country_col][0], str):
                            json_file["Country"] = json_file[country_col]
                        elif len(json_file[country_col]) >= 1 and isinstance(json_file[country_col], list):
                            if isinstance(json_file[country_col][0], dict) and (
                                "Country" in json_file[country_col][0] or "country" in json_file[country_col][0]
                            ):
                                json_file["Country"] = [d["Country"] for d in json_file[country_col]]
                            elif isinstance(json_file[country_col][0], dict) and (
                                "Country" not in json_file[country_col][0]
                                and "country" not in json_file[country_col][0]
                            ):
                                json_file["Country"] = list(json_file[country_col].keys())
                    except:
                        json_file["Country"] = []

                # todo: normalize location column in a similar way to country (probably?) when we start parsing locations
                # todo: normalize "n/a" as NULL
                # todo: normalize "Nationwide" for Location to be the same for Country column
                # normalize dates
                json_file["Event_Name"] = file_list[idx].split(".json")[0]
                if "Start_Date" in json_file.keys():
                    json_file["Start_Date"] = self.infer_date_from_dict(json_file["Start_Date"])
                if "End_Date" in json_file.keys():
                    json_file["End_Date"] = self.infer_date_from_dict(json_file["End_Date"])

                # rename the URL column to Source
                if "URL" in json_file.keys():
                    json_file["Source"] = json_file["URL"]
                    del json_file["URL"]

                dfs.append(json_file)

            except BaseException as err:
                self.logger.debug(f"JSON File {type(json_file)}\n{json_file}")
                self.logger.error(err)

        return dfs

    def save_json(
        self,
        dfs: list[pd.DataFrame],
        model_name: str,
        output_dir: str,
        columns: list[str] = [
            "Source",
            "Event_ID",
            "Event_Name",
            "Main_Event",
            "Main_Event_Assessment_With_Annotation",
            "Start_Date",
            "End_Date",
            "Time_with_Annotation",
            "Country",
            "Countries_Affected",
            "Country_with_Annotation",
            "Total_Summary_Death",
            "Specific_Instance_Per_Country_Death",
            "Total_Summary_Damage",
            "Total_Damage",
            "Total_Damage_Unit",
            "Total_Damage_Inflation_Adjusted",
            "Total_Damage_Inflation_Adjusted_Year",
        ],
    ) -> str:
        """
        Takes a list of dataframes, merges it into a single file, and stores file in output_dir with the correct set and model names
        """
        captured_columns = set([x for xs in [df.keys() for df in dfs] for x in xs])
        self.logger.info(f"Captured Columns: {captured_columns}")
        model_output = pd.DataFrame(dfs, columns=[c for c in columns if c in captured_columns])
        filename = f"{output_dir}/{model_name}.json"
        model_output.to_json(
            filename,
            orient="records",
        )
        return filename

    def normalize_column_names(self, json_file_path: str, output_file_path: str) -> None:
        """Normalizes column names when an LLM hallucinates alternative column names for a category.
           Solves the inconsistency of data type of some categories.

        Handles cases:
            - "time_information" nesting: ["start_date", "end_date", "time_with_annotation"]
            - "location_information" nesting: ["location", "location_with_annotation"]
            - "Administrative_Areas" : when it's a str, convert to a list, or when this item is not in the raw output, add it in the fixed output as an empty list
            - "Administrative_Areas_Annotation": when this item is not in the raw output, add it as a str NULL
            - "Locations" : when it's a str, convert to a list

        """

        raw_sys_output = json.load(open(json_file_path))

        nested_keys = ["time_information", "location_information"]
        incorrect_type_keys = ["Administrative_Areas"]
        missing_keys = ["Administrative_Areas", "Administrative_Areas_Annotation"]
        output_json = []
        for entry in raw_sys_output:
            output = {}
            for k in entry.keys():
                if k.lower() in nested_keys:
                    if isinstance(entry[k], dict):
                        if any(
                            [
                                x in [y.lower() for y in entry[k].keys()]
                                for x in ["start_date", "end_date", "time_with_annotation"]
                            ]
                        ) or any(
                            [
                                x in [y.lower() for y in entry[k].keys()]
                                for x in [
                                    "location",
                                    "location_with_annotation",
                                    "administrative_areas",
                                    "administrative_areas_annotation",
                                ]
                            ]
                        ):
                            for _k in entry[k]:
                                output[_k] = entry[k][_k]

                if k in incorrect_type_keys:
                    if isinstance(entry[k], str):
                        output[k] = [entry[k]]
                if "Specific_Instance_Per_Administrative_Area" in k:
                    if isinstance(entry[k], list):
                        for item in entry[k]:
                            if isinstance(item, dict) and isinstance(item.get("Locations"), str):
                                item["Locations"] = [item.get("Locations")]
                        output[k] = entry[k]
                if "Instance_Per_Administrative_Areas" in k:
                    if isinstance(entry[k], list):
                        for item in entry[k]:
                            if isinstance(item, dict) and isinstance(item.get("Administrative_Areas"), str):
                                item["Administrative_Areas"] = [item.get("Administrative_Areas")]
                        output[k] = entry[k]
                else:
                    output[k] = entry[k]
            for k in missing_keys:
                if k in entry.keys():
                    if isinstance(entry[k], dict):
                        for key_name in missing_keys:
                            if key_name in entry[k].keys():
                                output[key_name] = entry[k][key_name]

                if k not in entry.keys() and k not in output.keys():
                    if k == "Administrative_Areas":
                        output[k] = []
                    elif k == "Administrative_Areas_Annotation":
                        output[k] = "NULL"

            output_json.append(output)

        with open(output_file_path, "w") as fp:
            json.dump(output_json, fp)

        self.logger.info(f"Stored output in {output_file_path}")

    def normalize_lists_of_num(self, json_file_path: str, output_file_path: str, locale_config: str) -> None:
        raw_sys_output = json.load(open(json_file_path))
        output_json = []
        norm_utils = NormalizeUtils()
        nlp = norm_utils.load_spacy_model()
        norm_num = NormalizeNumber(nlp, locale_config=locale_config)
        for entry in raw_sys_output:
            output = {}
            target_keys = [x for x in entry.keys() if x.startswith("Specific_Instance_") or x.startswith("Instance_")]

            for k in [x for x in entry.keys() if entry[x] is not None]:
                if k in target_keys:
                    for rec in range(len(entry[k])):
                        records = []
                        if "Num" in entry[k][rec]:
                            if isinstance(entry[k][rec]["Num"], list):
                                normalized = []
                                for n in entry[k][rec]["Num"]:
                                    _min, _max, _ = norm_num.extract_numbers(n)
                                    if _min and _max:
                                        normalized.append((_min, _max))
                                nomralized_num = (
                                    f"{sum([x[0] for x in normalized if isinstance(x[0], (int, float))])}-{sum([x[1] for x in normalized if isinstance(x[1], (int, float))])}"
                                    if normalized
                                    else "NULL"
                                )
                                entry[k][rec]["Num"] = nomralized_num
                                records.append(entry[k][rec])

                            elif isinstance(entry[k][rec]["Num"], str):
                                records.append(entry[k][rec])
                    output[k] = entry[k]
                else:
                    output[k] = entry[k]

            output_json.append(output)
        with open(output_file_path, "w") as fp:
            json.dump(output_json, fp, indent=3)

        self.logger.info(f"Stored output in {output_file_path}")


class GeoJsonUtils:
    def __init__(self, nid_path: str = "/tmp/geojson") -> None:
        self.logger = Logging.get_logger("normalize-utils-json", level="DEBUG")
        self.logger.info(f"Loading nids from {nid_path}")
        self.nid_path = f"{nid_path}/geojson"
        self.non_english_nids_path = f"{nid_path}/non-english-locations.csv"
        self.non_english_nids_columns = ["location_name", "nid"]
        pathlib.Path(self.nid_path).mkdir(parents=True, exist_ok=True)
        self.nid_list = self.update_nid_list()
        try:
            self.non_english_nids_df = pd.read_csv(
                self.non_english_nids_path,
                sep=",",
            )
        except BaseException as err:
            self.non_english_nids_df = pd.DataFrame(columns=self.non_english_nids_columns)
            self.logger.debug(f"Could not load nids csv. Error: {err}")

    def update_nid_list(self) -> None:
        self.nid_list = os.listdir(self.nid_path)
        self.logger.debug(f"Found {len(self.nid_list)} nids in {self.nid_path}")
        if not self.nid_list:
            self.logger.warning(
                f"Could not load nids! Directory may be empty. Using the empty directory {self.nid_path}"
            )
        self.nid_list = []

    def random_nid(self, length: int = 5) -> str:
        """Generates a short lowercase UID"""
        return shortuuid.ShortUUID().random(length=length)

    def generate_nid(self, text: str) -> tuple[str, None]:
        nid = None
        try:
            assert text
            text = unidecode(text)
            text.encode(encoding="utf-8").decode("ascii")
            nid = text
        except AssertionError as err:
            self.logger.error(f"`{text}` not valid: {type(text)}. Error: {err}")
        except UnicodeDecodeError as err:
            self.logger.error(f"`{text}` could not be decoded to ascii. Error: {err}")

        if not nid:
            if text in self.non_english_nids_df["location_name"]:
                nid = self.non_english_nids_df[self.non_english_nids_df["location_name"] == text].tolist()[-1]
            else:
                nid = self.random_nid(length=12)
                self.non_english_nids_df = pd.concat(
                    [
                        self.non_english_nids_df,
                        pd.DataFrame([[nid, text]], columns=self.non_english_nids_columns),
                    ],
                    ignore_index=True,
                )
        return re.sub("\W|^(?=\d)", "-", nid.lower())

    def store_non_english_nids(self) -> None:
        self.logger.info(f"Storing non english location names and their generated nids to {self.non_english_nids_path}")
        self.non_english_nids_df.to_csv(self.non_english_nids_path, sep=",", index=False, mode="w")

    def check_duplicate(self, nid: str, obj: json) -> tuple[str, bool]:
        nid_path = f"{self.nid_path}/{nid}"
        self.update_nid_list()

        if nid_path in self.nid_list or nid in self.non_english_nids_df["location_name"].tolist():
            try:
                assert obj == json.load(nid_path)
                return nid, True
            except AssertionError as err:
                self.logger.error(f"Duplicate name but different content for {nid_path}")
                self.logger.debug(f"Error: {err}")
                alt_nid = self.generate_nid(f"{nid}-{self.random_nid(5)}" if nid else self.random_nid(length=12))
                return alt_nid, False
        return nid, False

    def geojson_to_file(self, geojson_obj: str, area_name: str) -> str:
        """Checks if a GeoJson object is stored by a specific nid. Handles three cases:
        - If the nid and file content match, nothing is written to file.
        - If the there is no record of the nid in self.nid_path, a new file is written.

        # the last one would reveal problems with this approach, but gotta test first to see
        - If the nid matches a file name but the content is different, create an extended nid name and store it.

        Returns the nid used to store to file
        """
        if not area_name or not geojson_obj:
            return None

        nid = self.generate_nid(area_name)
        try:
            geojson_obj = ast.literal_eval(geojson_obj)
            nid, dup = self.check_duplicate(nid, geojson_obj)
            if not dup:
                with open(f"{self.nid_path}/{nid}.json", "w") as f:
                    json.dump(geojson_obj, f)
        except BaseException as err:
            self.logger.debug(f"Could not process GeoJson to file. Error: {err}")
            return None
        return nid


class CategoricalValidation:
    def __init__(self):
        self.logger = Logging.get_logger("categorical-validation-utils")
        self.main_event_categories = {
            "Flood": ["Flood"],
            "Extratropical Storm/Cyclone": ["Wind", "Flood", "Blizzard", "Hail"],
            "Tropical Storm/Cyclone": ["Wind", "Flood", "Lightning"],
            "Extreme Temperature": ["Heatwave", "Cold Spell"],
            "Drought": ["Drought"],
            "Wildfire": ["Wildfire"],
            "Tornado": ["Wind"],
        }

        self.hazards_categories = [
            "Wind",
            "Flood",
            "Blizzard",
            "Hail",
            "Drought",
            "Heatwave",
            "Lightning",
            "Cold Spell",
            "Wildfire",
        ]

    def validate_categorical(self, text: str, categories: list) -> str | None:
        try:
            cat_idx = [x.lower() for x in categories].index(text.lower())
            return categories[cat_idx]
        except BaseException as err:
            self.logger.warning(f"Value `{text}` may be invalid for this category. Error: {err}")
            return

    def validate_main_event_hazard_relation(
        self, row: dict, hazards: str = "Hazards", main_event: str = "Main_Event"
    ) -> dict:
        try:
            related_hazards = [x for x in self.main_event_categories[row[main_event]]]
            row[hazards] = list(set([h for h in row[hazards] if h.lower() in [x.lower() for x in related_hazards]]))
        except BaseException as err:
            self.logger.error(f"Could not validate relationship between {hazards} and {main_event}. Error: {err}")
        return row

    def validate_currency_monetary_impact(self, row: dict) -> dict:
        cols = ["Total_{}_Min", "Total_{}_Max", "Total_{}_Approx", "Total_{}_Unit", "Total_{}_Inflation_Adjusted"]

        for category in ["Damage", "Insured_Damage"]:
            try:
                Currency(row[f"Total_{category}_Unit"])
            except ValueError as err:
                self.logger.error(f"""Invalid currency {row[f"Total_{category}_Unit"]}. Error: {err}""")
                for c in cols:
                    cat = c.format(category)
                    row[cat] = None
        return row
