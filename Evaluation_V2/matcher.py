from statistics import mean

from Evaluation_V2.comparer import Comparer
from Evaluation_V2.utils import Logging


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
        #update in v2 
        self.GID_cat: dict[str, int] = {"Locations_GID": 1}
        self.list_cat: dict[str, int] = {"Locations_Norm":1}
        self.set_cat:  dict[str, int] ={"Administrative_Area_GID": 1}
        self.str_cat:dict[str, int] = { "Administrative_Area_Norm": 1}
        self.comp = Comparer(null_penalty, [])

    @staticmethod
    def create_pad(specific_instance: dict) -> dict:
        padded = {}
        for k in specific_instance.keys():
            # preserve "Event_ID"
            padded[k] = specific_instance[k] if k == "Event_ID" else None
        return padded

    def calc_similarity(self, gold_instance: dict, sys_list: list) -> list[float]:
        score_list = []
        event_id = gold_instance.get("Event_ID", "Unknown")

        for si in sys_list:
            scores = []
            skip_instance = False  # Flag to skip further processing for this instance

            for k in gold_instance.keys():
                try:
                    # Check str_cat and set_cat first
                    if k in self.str_cat or k in self.set_cat:
                        r1 = self.comp.string(gold_instance[k], si[k]) if k in self.str_cat else None
                        r2 = self.comp.sequence(gold_instance[k], si[k]) if k in self.set_cat else None

                        valid_scores = [x for x in [r1, r2] if x is not None]
                        r = min(valid_scores) if valid_scores else None
                        

                        # If r is not None and not 0, skip this instance and set score to 0
                        if r is not None and r != 0:
                            scores = [0]  # Set score to 0 for this instance
                            skip_instance = True
                            break  # Exit the field loop for this instance

                        if r == 0:
                            continue  # Skip to the next field

                    # Handle GID_cat and list_cat
                    if k in self.GID_cat or k in self.list_cat:
                        r1 = self.comp.compare_gid_lists(gold_instance[k], si[k]) if k in self.GID_cat else None
                        r2 = self.comp.sequence(gold_instance[k], si[k]) if k in self.list_cat else None
                        valid_scores = [x for x in [r1, r2] if x is not None]
                        r = min(valid_scores) if valid_scores else None
                        

                    # Handle int_cat
                    if k in self.int_cat:
                        try:
                            if isinstance(int(gold_instance[k]), int):
                                r = self.comp.integer(gold_instance[k], si[k])
                               
                        except:
                            pass

                    # Append the computed score
                    if r is not None:
                        scores.append(1 - (r * self.int_cat.get(k)))  # Default weight of 1.0 if key not found
                        

                except Exception as e:
                    if k != "Event_ID":
                        self.logger.debug(f"Unsupported column name: {k} will be ignored during matching. Error: {e}")

            # If the instance was skipped, append 0; otherwise, append the mean score
            if skip_instance:
                score_list.append(0)
            else:
                score_list.append(mean(scores) if scores else 0)

        
        return score_list
        """
    def calc_similarity(self, gold_instance: dict, sys_list: list) -> list[float]:
        score_list = []
        event_id = gold_instance.get("Event_ID", "Unknown")
        for si in sys_list:
            scores = []
            for k in gold_instance.keys():
                try: 
                    if k in self.str_cat or k in self.set_cat:
                        r1 = self.comp.string(gold_instance[k], si[k]) if k in self.str_cat else None
                        r2 = self.comp.sequence(gold_instance[k], si[k]) if k in self.set_cat else None
                        
                        valid_scores = [x for x in [r1, r2] if x is not None]
                        r = min(valid_scores) if valid_scores else None
                        print(f"Event_ID: {event_id}, field :{k}, admin score: {r}")
                    if r is not None and r != 0:
                        scores=len[0] * len(sys_list)
                        score_list.append(mean(scores))
                        return score_list
                        
                    if r == 0:
                            continue
                except:  
               
                    if k in self.GID_cat or k in self.list_cat:
                        r1 = self.comp.compare_gid_lists(gold_instance[k], si[k]) if k in self.GID_cat else None
                        r2 = self.comp.sequence(gold_instance[k], si[k]) if k in self.list_cat else None
                        valid_scores = [x for x in [r1, r2] if x is not None]
                        r = min(valid_scores) if valid_scores else None
                        print(f"Event_ID: {event_id}, field :{k},location score: {r}")
                    
                    if k in self.int_cat:
                        try:
                            if isinstance(int(gold_instance[k]), int):
                                r = self.comp.integer(gold_instance[k], si[k])
                                print(f"Event_ID: {event_id}, field :{k},int score: {r}")
                        except:
                            pass

                    try:
                        scores.append(1 - (r * self.int_cat[k]))
                    
                    except Exception:
                        if k != "Event_ID":
                            self.logger.debug(f"Unsupported column name: {k} will be ignored during matching.")

                score_list.append(mean(scores))
        print(f"Event_ID: {event_id},  score list: {score_list}")
        return score_list

        def calc_similarity(self, gold_instance: dict, sys_list: list) -> list[float]:
            score_list: float = []
            for si in sys_list:
                scores = []
                for k in gold_instance.keys():
                    try: 
                        if k in self.str_cat or k in self.set_cat:
                            r1, r2 = None, None  # Initialize r1 and r2

                            if k in self.str_cat:
                                r1 = self.comp.string(gold_instance[k], si[k])

                            if k in self.set_cat:
                                r2 = self.comp.sequence(gold_instance[k], si[k])

                            # If either r1 or r2 is 0, set r to 0
                            if (r1 is not None and r1 == 0) or (r2 is not None and r2 == 0):
                                r = 0
                            else:
                                # Get the minimum non-None value
                                valid_scores = [x for x in [r1, r2] if x is not None]
                                r = min(valid_scores) if valid_scores else None

                            # If the minimum score is not 0, treat as mismatch and return similarity score of 1 for the entire list
                            if r is not None and r != 0:
                                score_list= [1] * len(sys_list)
                                return score_list
                    except:
                            # If the minimum score is 0, continue with the next comparisons
                            if r == 0:
                                break

                    if k in self.GID_cat or k in self.list_cat:
                        r1, r2 = None, None  # Initialize r1 and r2

                        if k in self.GID_cat:
                            r1 = self.comp.compare_gid_lists(gold_instance[k], si[k])

                        if k in self.list_cat:
                            r2 = self.comp.sequence(gold_instance[k], si[k])

                        # If either r1 or r2 is 0, set r to 0
                        if (r1 is not None and r1 == 0) or (r2 is not None and r2 == 0):
                            r = 0
                        else:
                            # Get the minimum non-None value
                            valid_scores = [x for x in [r1, r2] if x is not None]
                            r = min(valid_scores) if valid_scores else None

                    if k in self.int_cat:
                        # Only include gold_instance[k] from numerical categories
                        # For monetary categories, gold_instance[k] is a list
                        # For numerical caterogies, it is always an int (or can be cast to an int)
                        try:
                            if isinstance(int(gold_instance[k]), int):
                                r = self.comp.integer(gold_instance[k], si[k])
                        except:
                            pass

                    try:
                        scores.append(1 - (r * self.int_cat[k]))
                        del r
                    except Exception:
                        if k != "Event_ID":
                            self.logger.debug(f"Unsupported column name: {k} will be ignored during matching.")

                score_list.append(mean(scores))

        # index of mean score corresponds to sys_list item
        return score_list
        """
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
        event_id = "Unknown"  # Default value in case of failure

        if isinstance(gold_list, list) and gold_list:  # Ensure gold_list is a non-empty list
            if isinstance(gold_list[0], dict):  # Ensure first item is a dictionary
                event_id = gold_list[0].get("Event_ID", "Unknown")
        gold, sys, similarity, gold_matched, sys_matched = [], [], [], [], []
        similarity_matrix = [self.calc_similarity(si, sys_list) for si in gold_list]
        best_matches = [
            (gi, si, similarity_matrix[gi][si])
            for gi in range(len(similarity_matrix))
            for si in range(len(similarity_matrix[gi]))
            if similarity_matrix[gi][si] > self.threshold
        ]
        best_matches.sort(key=lambda x: x[2], reverse=True)
        print(f"Event_ID: {event_id}, best_matches: {best_matches}")

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
                event_id = si.get("Event_ID", "Unknown")
                si["Event_ID"] = f"{event_id}-{counter}"
                counter += 1

        return (gold, sys)


class CurrencyMatcher:
    def __init__(self):
        pass

    @staticmethod
    def get_best_currency_match(sys_str: str, gold_list: list) -> int:
        for i in range(len(gold_list)):
            if gold_list[i] == sys_str:
                print("matching currency",i)
                return i
        return -1
