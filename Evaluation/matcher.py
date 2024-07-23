from statistics import mean

from Evaluation.comparer import Comparer
from Evaluation.utils import Logging


class SpecificInstanceMatcher:
    """Matches and pads specific instances (subevents) from two separate lists.
    'Padded' specific instances will have NoneType objects as values"""

    def __init__(self, threshold: float = 0.6):
        self.logger = Logging.get_logger("specific instance matcher")

        self.threshold = threshold
        self.int_cat: list[str] = [
            "Num_Min",
            "Num_Max",
            "Adjusted_Year",
            "Start_Date_Day",
            "Start_Date_Month",
            "Start_Date_Year",
            "End_Date_Day",
            "End_Date_Month",
            "End_Date_Year",
        ]
        self.bool_cat: list[str] = ["Adjusted"]
        self.str_cat: list[str] = ["Country_Norm", "Unit"]
        self.list_cat: list[str] = ["Location_Norm"]

        self.comp = Comparer(0.5, [])

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
                    r = self.comp.integer(gold_instance[k], si[k])
                elif k in self.bool_cat:
                    r = self.comp.boolean(gold_instance[k], si[k])
                elif k in self.str_cat:
                    r = self.comp.string(gold_instance[k], si[k])
                elif k in self.list_cat:
                    r = self.comp.sequence(gold_instance[k], si[k])
                try:
                    scores.append(1 - r)
                    del r
                except Exception:
                    if k != "Event_ID":
                        self.logger.warning(
                            f"Unsupported column name: {k} will be ignored during matching."
                        )

            score_list.append(mean(scores))

        # index of mean score corresponds to sys_list item
        return score_list

    def schema_checker(self, gold_list: list[dict], sys_list: list[dict]) -> bool:
        for g in range(len(gold_list)):
            if sorted(gold_list[0].keys()) != sorted(gold_list[g].keys()):
                self.logger.error(
                    f"Gold file contains entries with inconsistent column names at specific instance #{g}: {gold_list[g].keys()}. Expected columns: {gold_list[0].keys()}"
                )
                return False

        for s in range(len(sys_list)):
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

        gold, sys, already_matched = [], [], []

        for si in gold_list:
            similarity = self.calc_similarity(si, sys_list)

            # create a list of indices of the matches sorted by value (best matches first)
            top_matches_sorted_indices = [i for i, x in sorted(enumerate(similarity), key=lambda x: x[1], reverse=True)]
            gold.append(si)
            for i in top_matches_sorted_indices:
                # inspect the best matches from the top
                # match if a specific instance meets the threshold & has not already been matched by another specific instance
                if similarity[i] >= self.threshold and i not in already_matched:
                    already_matched.append(i)
                    sys.append(sys_list[i])
                    break
                else:
                    # otherwise, create a "padded" match
                    sys.append(self.create_pad(si))
                    break

        # if any events in the sys output remain unmatched, create a "padded" match for them
        for si in sys_list:
            if si not in sys:
                sys.append(si)
                gold.append(self.create_pad(si))

        assert len(gold) == len(sys), AssertionError(
            f"Something went wrong! number of specific instances in gold: {len(gold)}; in sys: {len(sys)}"
        )

        for ds in [gold, sys]:
            counter = 0
            for si in ds:
                si["Event_ID"] = f"{si['Event_ID']}-{counter}"
                counter += 1

        return (gold, sys)
