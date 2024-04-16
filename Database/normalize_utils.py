import re
from typing import Tuple, Union

import pandas as pd
import shortuuid
from dateparser.date import DateDataParser


class NormalizeUtils:
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

    @staticmethod
    def normalize_date(row: Union[str, None]) -> Tuple[int, int, int]:
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
                print(f"Date parsing error in {row} with date\n{err}\n")
                return (None, None, None)

    @staticmethod
    def unpack_col(df: pd.DataFrame, columns: list = []) -> pd.DataFrame:
        """Unpacks Total_Summary_* columns"""
        for c in columns:
            df = pd.concat([pd.json_normalize(df[c]), df], axis=1)
            df.drop(columns=[c], inplace=True)
        return df
