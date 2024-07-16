from statistics import mean


class SpecificInstanceMatcher:
    """Matches and pads specific instances (subevents) from two separate lists.
    'Padded' specific instances will have NoneType objects as values"""

    def __init__(self, threshold: float = 0.66):
        self.threshold = threshold
        self.int_cat: list[str] = [
            "Num_Min",
            "Num_Max",
            "Specific_Instance_Year",  # check name for year
            "Start_Date_Day",
            "Start_Date_Month",
            "Start_Date_Year",
            "End_Date_Day",
            "End_Date_Month",
            "End_Date_Year",
        ]  # consider day or not?
        self.bool_cat: list[str] = [
            "Specific_Instance_Adjusted"
        ]  # check name for adjusted
        self.str_cat: list[str] = ["Country_Norm", "Specific_Instance_Unit"]
        self.list_cat: list[str] = ["Location_Norm"]

    @staticmethod
    def create_pad(specific_instance: dict) -> dict:
        padded = {}
        for k in specific_instance.keys():
            padded[k] = None

        return padded

    def calc_similarity(self, gold_instance: dict, sys_list: list) -> list[float]:
        score_list: float = []

        for si in sys_list:
            scores = []
            for k in gold_instance.keys():
                scores.append(1) if gold_instance[k] == si[k] else scores.append(0)

            score_list.append(mean(scores))
            del scores  # avoid this leaking, may remove later

        # index of mean score corresponds to sys_list item
        return score_list

