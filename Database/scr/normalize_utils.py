import ast
import json
import logging
import os
import re
from typing import Tuple, Union

import pandas as pd
import pycountry
import shortuuid
from dateparser.date import DateDataParser
from dateparser.search import search_dates
from spacy import language as spacy_language


class Logging:
    @staticmethod
    def get_logger(name: str, level: str = logging.INFO) -> logging.Logger:
        """
        A function that handles logging in all database src functions.
        Change the level to logging.DEBUG when debugging.
        """
        logging.basicConfig(
            format="%(name)s: %(asctime)s %(levelname)-8s %(message)s",
            level=level,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        return logging.getLogger(name)


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
            json_normalized_df = json_normalized_df[
                [x for x in json_normalized_df.columns if not str(x).startswith("Specific_")] # in case the x is not string 
            ]
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
    def simple_country_check(c: str):
        try:
            exists = pycountry.countries.get(name=c)
            if exists:
                return True
        except:
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
            "Total_Damage_Units",
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