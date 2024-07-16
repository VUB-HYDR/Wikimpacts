from statistics import mean

# from Evaluation.comparer import Comparer


class SpecificInstanceMatcher:
    """Matches and pads specific instances (subevents) from two separate lists.
    'Padded' specific instances will have NoneType objects as values"""

    def __init__(self, threshold: float = 0.75):
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

    def match(self, gold_list: list[dict], sys_list: list[dict]) -> tuple[list[dict]]:
        gold, sys, sim, already_matched = [], [], [], []  # N, M, M

        for si in gold_list:
            similarity = self.calc_similarity(si, sys_list)
            gold.append(si)
            best_match_index = similarity.index(max(similarity))
            if max(similarity) >= self.threshold and best_match_index not in already_matched:
                # returns index of the first max match only!
                # best_match = sys_list[best_match_index]
                # sim.append(similarity)  # as long as the sys list
                already_matched.append(similarity.index(max(similarity)))
                sys.append(sys_list[best_match_index])
            else:
                sys.append(self.create_pad(si))

        # print(sim)

        for i in range(len(gold)):
            print(gold[i], "--->", sys[i])
        return (gold, sys)


if __name__ == "__main__":
    matcher = SpecificInstanceMatcher()
    matcher.match(
        [
            {"Num_Min": 2, "Num_Max": 91, "Start_Date_Year": 2030},
            {"Num_Min": 2, "Num_Max": 91, "Start_Date_Year": 2030},
            {"Num_Min": 0, "Num_Max": 10, "Start_Date_Year": 2031},
        ],
        [
            {"Num_Min": 0, "Num_Max": 11, "Start_Date_Year": 2031},
            {"Num_Min": 0, "Num_Max": 11, "Start_Date_Year": 2021},
            {"Num_Min": 2, "Num_Max": 91, "Start_Date_Year": 2030},
            {"Num_Min": 7, "Num_Max": 30, "Start_Date_Year": 2030},
        ],
    )
