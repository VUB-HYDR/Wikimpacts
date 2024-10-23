from .log_utils import Logging


class DataGapUtils:
    def __init__(self):
        self.logger = Logging.get_logger("data-gap-utils")

    @staticmethod
    def fill_date(row: dict, replace_with_date: dict):
        date_cols = [x for x in row.keys() if "_Date_" in x]
        if all([True if row[d] is None else False for d in date_cols]):
            for c in date_cols:
                row[c] = replace_with_date[c]
        return row
