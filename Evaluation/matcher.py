from statistics import mean

from Evaluation.comparer import Comparer
from Evaluation.utils import Logging


class SpecificInstanceMatcher:
    """Matches and pads specific instances (subevents) from two separate lists.
    'Padded' specific instances will have NoneType objects as values"""

    def __init__(self, threshold: float = 0.6, null_penalty: float = 0.5):
        self.logger = Logging.get_logger("specific instance matcher")
        self.logger.info(f"Null penalty: {null_penalty}; Threshold: {threshold}")
        self.threshold = threshold
        self.int_cat: dict[str, int] = {
            "Num_Min": 1,
            "Num_Max": 1,
            "Start_Date_Day": 0.125,
            "Start_Date_Month": 0.125,
            "Start_Date_Year": 0.125,
            "End_Date_Day": 0.125,
            "End_Date_Month": 0.125,
            "End_Date_Year": 0.125,
        }
        self.bool_cat: list[str] = []
        self.str_cat: dict[str, int] = {"Administrative_Area_Norm": 1}
        self.list_cat: dict[str, int] = {"Locations_Norm": 1, "Administrative_Areas_Norm": 1}

        self.comp = Comparer(null_penalty, [])

    @staticmethod
    def create_pad(specific_instance: dict) -> dict:
        padded = {}
        for k in specific_instance.keys():
            # preserve "Event_D"
            padded[k] = specific_instance[k] if k == "Event_ID" else None
        return padded

    def calc_similarity(self, gold_instance: dict, sys_list: list) -> list[float]:
        score_list: float = []
        for si in sys_list:
            scores = []
            for k in gold_instance.keys():
                if k in self.int_cat:
                    # Only include gold_instance[k] from numerical categories
                    # For monetary categories, gold_instance[k] is a list
                    # For numerical caterogies, it is always an int (or can be cast to an int)
                    try:
                        if isinstance(int(gold_instance[k]), int):
                            r = self.comp.integer(gold_instance[k], si[k])
                    except:
                        pass
                elif k in self.str_cat:
                    r = self.comp.string(gold_instance[k], si[k])
                elif k in self.list_cat:
                    r = self.comp.sequence(gold_instance[k], si[k])
                try:
                    scores.append(1 - (r * self.int_cat[k]))
                    del r
                except Exception:
                    if k != "Event_ID":
                        self.logger.debug(f"Unsupported column name: {k} will be ignored during matching.")

            score_list.append(mean(scores))

        # index of mean score corresponds to sys_list item
        return score_list

    def schema_checker(self, gold_list: list[dict], sys_list: list[dict]) -> bool:
        # in case the sys output or gold is an empty list
        if len(gold_list) == 0 or len(sys_list) == 0:
            return True

        for g in range(len(gold_list)):
            # check that all column names in the gold are consistent
            if sorted(gold_list[0].keys()) != sorted(gold_list[g].keys()):
                self.logger.error(
                    f"Gold file contains entries with inconsistent column names at specific instance #{g}: {gold_list[g].keys()}. Expected columns: {gold_list[0].keys()}"
                )
                return False

        for s in range(len(sys_list)):
            # if all gold columns are consistent, check that they are consistent with the sys_list ones
            try:
                assert all([e in sys_list[s].keys() for e in gold_list[0].keys()])
                return True
            except Exception:
                self.logger.error(
                    f"Inconsistent columns found in sys file!: {[e for e in sys_list[s].keys() if e not in gold_list[0].keys()]}"
                )
                return False

    def match(self, gold_list: list[dict], sys_list: list[dict]) -> tuple[list[dict]]:
        if self.schema_checker(gold_list, sys_list) != True:
            self.logger.error("Please check the column names in your gold and sys files.")
            raise BaseException

        gold, sys, similarity, gold_matched, sys_matched = [], [], [], [], []
        similarity_matrix = [self.calc_similarity(si, sys_list) for si in gold_list]
        best_matches = [
            (gi, si, similarity_matrix[gi][si])
            for gi in range(len(similarity_matrix))
            for si in range(len(similarity_matrix[gi]))
            if similarity_matrix[gi][si] > self.threshold
        ]
        best_matches.sort(key=lambda x: x[2], reverse=True)

        # find the best matches in the similarity matrix
        for gi, si, sim in best_matches:
            if gi not in gold_matched and si not in sys_matched:
                gold.append(gold_list[gi])
                sys.append(sys_list[si])
                gold_matched.append(gi)
                sys_matched.append(si)
                similarity.append(sim)

        # pad remaining unmatched specific instances
        for gi in range(len(gold_list)):
            if gi not in gold_matched:
                gold.append(gold_list[gi])
                sys.append(self.create_pad(gold_list[gi]))

        for si in range(len(sys_list)):
            if si not in sys_matched:
                sys.append(sys_list[si])
                gold.append(self.create_pad(sys_list[si]))

        assert len(gold) == len(sys), AssertionError(
            f"Something went wrong! number of specific instances in gold: {len(gold)}; in sys: {len(sys)}"
        )

        for ds in [gold, sys]:
            counter = 0
            for si in ds:
                si["Event_ID"] = f"{si['Event_ID']}-{counter}"
                counter += 1

        return (gold, sys)


class CurrencyMatcher:
    def __init__(self):
        pass

    @staticmethod
    def clean_currency(value):
        # Check if the value is a byte-encoded string
        if isinstance(value, bytes):
            value = value.decode("utf-8")  # Decode to string

    @staticmethod
    def get_best_currency_match(sys_str: str, gold_list: list) -> str:
        # Loop through the gold list, cleaning each entry, and compare with the clean sys_str
        for i in range(len(gold_list)):
            clean_gold = CurrencyMatcher.clean_currency(gold_list[i])
            print(clean_gold)
            if clean_gold == CurrencyMatcher.clean_currency(sys_str):
                return i
        return -1
