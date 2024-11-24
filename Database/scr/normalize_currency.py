import os

import pandas as pd

from .log_utils import Logging


class CurrencyBase:
    def __init__(self) -> None:
        # column names
        self.num_min: str = "Num_Min"
        self.num_max: str = "Num_Max"
        self.num_approx: str = "Num_Approx"
        self.num_unit: str = "Num_Unit"
        self.num_inflation_adjusted: str = "Num_Inflation_Adjusted"
        self.num_inflation_adjusted_year: str = "Num_Inflation_Adjusted_Year"
        self.t_num_min: str = "Total_{}_Min"
        self.t_num_max: str = "Total_{}_Max"
        self.t_num_approx: str = "Total_{}_Approx"
        self.t_num_unit: str = "Total_{}_Unit"
        self.t_num_inflation_adjusted: str = "Total_{}_Inflation_Adjusted"
        self.t_num_inflation_adjusted_year: str = "Total_{}_Inflation_Adjusted_Year"
        self.start_date_year: str = "Start_Date_Year"
        self.end_date_year: str = "End_Date_Year"
        self.start_date_month: str = "Start_Date_Month"
        self.end_date_month: str = "End_Date_Month"

        # valid categories
        self.monetary_categories: tuple = ("Damage", "Insured_Damage")

        # currencies
        self.usd = "USD"


class InflationAdjustment(CurrencyBase):
    def __init__(self) -> None:
        super().__init__()
        self.logger = Logging.get_logger("inflation-adjustment-utils")
        self.inflation_index_2024: pd.DataFrame = pd.read_csv(
            "Database/data/currency/inflation_Index_2024.csv", header=0
        )

    def adjust_inflation_USD_2024(self, amount: float, year: int) -> float | None:
        try:
            if isinstance(year, str):
                year = int(year)
            assert year in self.inflation_index_2024.Year.to_list()
            x_index = (
                self.inflation_index_2024.loc[self.inflation_index_2024.Year == year].reset_index().CPI_2024_base[0]
            )
            return amount * (100 / x_index)
        except BaseException as err:
            self.logger.error(f"Could not adjust amount {amount} for year {year}. Error: {err}")
            return None
            # return amount

    def adjust_inflation_row_USD_2024(self, row: dict, l1_impact: None | str) -> dict:
        num_min, num_max, num_approx, num_inflation_adjusted, num_inflation_adjusted_year = (
            self.num_min,
            self.num_max,
            self.num_approx,
            self.num_inflation_adjusted,
            self.num_inflation_adjusted_year,
        )
        if l1_impact in self.monetary_categories:
            num_min, num_max, num_approx, num_inflation_adjusted, num_inflation_adjusted_year = (
                self.t_num_min.format(l1_impact),
                self.t_num_max.format(l1_impact),
                self.t_num_approx.format(l1_impact),
                self.t_num_inflation_adjusted.format(l1_impact),
                self.t_num_inflation_adjusted_year.format(l1_impact),
            )

        year = None
        # use the inflation adjustment year if inflation adjustment is True
        if row[num_inflation_adjusted_year] and row[num_inflation_adjusted]:
            year = row[num_inflation_adjusted_year]
        # otherwise, use the end year if present
        elif row[self.end_date_year]:
            year = row[self.end_date_year]
        # otherwise, use the start year if present
        elif row[self.start_date_year]:
            year = row[self.start_date_year]

        if year:
            _min, _max = self.adjust_inflation_USD_2024(row[num_min], year=year), self.adjust_inflation_USD_2024(
                row[num_max], year=year
            )
            if _min and _max:
                row[num_min] = _min
                row[num_max] = _max
                row[num_approx] = 1  # adjusted value are all approximations
                row[num_inflation_adjusted] = 1
                row[num_inflation_adjusted_year] = 2024
        else:
            self.logger.debug(f"Could not adjust inflation to USD 2024 since no year can be inferred. Row: {dict(row)}")
        return row


class CurrencyConversion(CurrencyBase):
    def __init__(self) -> None:
        super().__init__()
        self.logger = Logging.get_logger("currency-conversion-utils")
        self.currency_conversion_path: str = "Database/data/currency/currency_conversion"
        self.currency_converstion_yearly_avg_path: str = "Database/data/currency/currency_conversion_yearly_avg"
        self.currency_conversion_yearly_avg: dict[str, pd.DataFrame] = {}
        self.currency_conversion: dict[str, pd.DataFrame] = {}
        currency_conversion_files = os.listdir(self.currency_conversion_path)
        currency_conversion_yearly_avg_files = os.listdir(self.currency_converstion_yearly_avg_path)

        for f in currency_conversion_files:
            self.currency_conversion[f.split("-")[0]] = pd.read_csv(f"{self.currency_conversion_path}/{f}", header=0)

        for f in currency_conversion_yearly_avg_files:
            self.currency_conversion_yearly_avg[f.split("-")[0]] = pd.read_csv(
                f"{self.currency_converstion_yearly_avg_path}/{f}", header=0
            )

    def convert_to_USD(self, currency: str, amount: float, year: int, month: int) -> float:
        try:
            # ensure the currency is availble
            assert currency in self.currency_conversion.keys()

            if isinstance(year, str):
                year = int(year)

            if isinstance(month, str):
                month = int(month)

            # validate year range based on the currency
            assert year <= self.currency_conversion[currency].Year.max()
            assert year >= self.currency_conversion[currency].Year.min()

            # ensure conversion data for the selected months exist
            assert month <= 12
            assert (
                month
                in self.currency_conversion[currency]
                .loc[(self.currency_conversion[currency].Year == year)]
                .Month.tolist()
            )

            # extract rate
            rate = (
                self.currency_conversion[currency]
                .loc[
                    (self.currency_conversion[currency].Year == year)
                    & (self.currency_conversion[currency].Month == month)
                ]
                .Rate.tolist()[0]
            )
            return amount / rate
        except BaseException as err:
            self.logger.error(f"Could not convert to USD (monthly average). Error: {err}")
            return amount

    def convert_to_USD_yearly_avg(self, currency: str, amount: float, year: int):
        try:
            if isinstance(year, str):
                year = int(year)
            # ensure the currency is availble
            assert currency in self.currency_conversion_yearly_avg.keys()
            # validate year range based on the currency
            assert year <= self.currency_conversion_yearly_avg[currency].Year.max()
            assert year >= self.currency_conversion_yearly_avg[currency].Year.min()

            # extract rate
            rate = (
                self.currency_conversion_yearly_avg[currency]
                .loc[self.currency_conversion_yearly_avg[currency].Year == year]
                .Rate.tolist()[0]
            )
            return amount / rate
        except BaseException as err:
            self.logger.error(f"Could not convert to USD (yearly average). Error: {err}")
            return amount

    def normalize_row_USD(self, row: dict, l1_impact: None | str) -> dict:
        num_min, num_max, num_unit, num_approx, num_inflation_adjusted, num_inflation_adjusted_year = (
            self.num_min,
            self.num_max,
            self.num_unit,
            self.num_approx,
            self.num_inflation_adjusted,
            self.num_inflation_adjusted_year,
        )
        if l1_impact in self.monetary_categories:
            num_min, num_max, num_unit, num_approx, num_inflation_adjusted, num_inflation_adjusted_year = (
                self.t_num_min.format(l1_impact),
                self.t_num_max.format(l1_impact),
                self.t_num_unit.format(l1_impact),
                self.t_num_approx.format(l1_impact),
                self.t_num_inflation_adjusted.format(l1_impact),
                self.t_num_inflation_adjusted_year.format(l1_impact),
            )

        if not row[num_unit]:
            self.logger.debug(f"Row has no currency. The row will be returned unchanged: {dict(row)}")
            return row
        if row[num_unit] == self.usd:
            self.logger.debug(f"Row already in USD. The row will be returned unchanged: {dict(row)}")
            return row
        year, month = None, None
        # use the inflation adjustment year if inflation adjustment is True
        if row[num_inflation_adjusted_year] and row[num_inflation_adjusted]:
            year = row[num_inflation_adjusted_year]
        # otherwise, use the end year if present
        elif row[self.end_date_year]:
            year = row[self.end_date_year]
        # otherwise, use the start year if present
        elif row[self.start_date_year]:
            year = row[self.start_date_year]

        # if thee is an inflation adjustment year and inflation adjustment is True:
        if row[num_inflation_adjusted_year] and row[num_inflation_adjusted]:
            # use the end month if the inflation adjusted year is the same as the end_date
            if row[num_inflation_adjusted_year] == row[self.end_date_year]:
                month = row[self.end_date_month]
            # otherwise, use the start month if it matches the inflation adjustment year
            elif row[num_inflation_adjusted_year] == row[self.start_date_year]:
                month = row[self.start_date_month]

        # otherwise, no month is set, so the yearly average rate will be used for the conversion

        if year:
            if month:
                row[num_min] = self.convert_to_USD(row[num_unit], row[num_min], year=year, month=month)
                row[num_max] = self.convert_to_USD(row[num_unit], row[num_max], year=year, month=month)
            elif not month:
                row[num_min] = self.convert_to_USD_yearly_avg(row[num_unit], row[num_min], year=year)
                row[num_max] = self.convert_to_USD_yearly_avg(row[num_unit], row[num_max], year=year)
            row[num_approx] = 1  # adjusted value are all approximations
            row[num_unit] = self.usd
            row[num_inflation_adjusted] = 1
            row[num_inflation_adjusted_year] = year
        else:
            self.logger.debug(f"Could not convert to USD since no year can be inferred. Row: {dict(row)}")
        return row
