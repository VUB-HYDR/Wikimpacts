from statistics import mean

import Evaluation.comparer as comparer


class SpecificInstanceMatcher:
    """Matches and pads specific instances (subevents) from two separate lists.
    'Padded' specific instances will have NoneType objects as values"""

    def __init__(self, threshold: float = 0.6):
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
        self.bool_cat: list[str] = ["Specific_Instance_Adjusted"]  # check name for adjusted
        self.str_cat: list[str] = ["Country_Norm", "Specific_Instance_Unit"]
        self.list_cat: list[str] = ["Location_Norm"]

        self.comp = comparer.Comparer(1, [])

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
                if k in self.int_cat:
                    r = self.comp.integer(gold_instance[k], si[k])
                elif k in self.bool_cat:
                    r = self.comp.boolean(gold_instance[k], si[k])
                elif k in self.str_cat:
                    r = self.comp.string(gold_instance[k], si[k])
                elif k in self.list_cat:
                    r = self.comp.sequence(gold_instance[k], si[k])
                scores.append(1 - r)

            score_list.append(mean(scores))
            del scores  # avoid this leaking, may remove later

        # index of mean score corresponds to sys_list item
        return score_list

    def match(self, gold_list: list[dict], sys_list: list[dict]) -> tuple[list[dict]]:
        gold, sys, already_matched = [], [], []

        for si in gold_list:
            gold.append(si)
            similarity = self.calc_similarity(si, sys_list)

            # create a list of indices of the matches sorted by value (best matches first)
            top_matches_sorted_indices = [i for i, x in sorted(enumerate(similarity), key=lambda x: x[1], reverse=True)]

            for i in top_matches_sorted_indices:
                # inspect the best matches from the top
                # match if a specific instance meets the threshold & has not already been matched by another specific instance
                if similarity[i] >= self.threshold and similarity[i] not in already_matched:
                    already_matched.append(similarity[i])
                    sys.append(sys_list[i])
                    break
                else:
                    # otherwise, create a "padded" match
                    sys.append(self.create_pad(si))

        # if any events in the sys output remain unmatched, create a "padded" match for them
        for si in sys_list:
            if si not in sys:
                sys.append(si)
                gold.append(self.create_pad(si))

        return (gold, sys)


if __name__ == "__main__":
    matcher = SpecificInstanceMatcher()
    matcher.match(
        [
            {
                "Num_Min": 2,
                "Num_Max": 82,
                "Start_Date_Year": 2030,
                "Location_Norm": ["Amman", "Zarqa"],
            },
            {
                "Num_Min": 2,
                "Num_Max": 91,
                "Start_Date_Year": 2030,
                "Location_Norm": ["Uppsala", "Stockholm"],
            },
            {
                "Num_Min": 0,
                "Num_Max": 10,
                "Start_Date_Year": 2031,
                "Location_Norm": ["Paris", "Lyon"],
            },
        ],
        [
            {
                "Num_Min": 0,
                "Num_Max": 11,
                "Start_Date_Year": 2031,
                "Location_Norm": ["Lyon"],
            },
            {
                "Num_Min": 1,
                "Num_Max": 84,
                "Start_Date_Year": 2029,
                "Location_Norm": ["Uppsala", "Zarqa"],
            },
            {
                "Num_Min": 2,
                "Num_Max": 91,
                "Start_Date_Year": 2030,
                "Location_Norm": ["Stockholm"],
            },
            {
                "Num_Min": 7,
                "Num_Max": 30,
                "Start_Date_Year": 2030,
                "Location_Norm": ["Uppsala", "Linköping"],
            },
        ],
    )
