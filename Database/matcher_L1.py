from statistics import mean

from Evaluation_V2.comparer import Comparer
from Evaluation_V2.utils import Logging

# this script is adapt to find and match the dulicates in the whole database 
class SpecificInstanceMatcher:
    """Matches and pads specific instances (subevents) in one list.
    'Padded' specific instances will have NoneType objects as values"""

    def __init__(self, threshold: float = 0.6, null_penalty: float = 0.5):
        self.logger = Logging.get_logger("specific instance matcher")
        self.logger.info(f"Null penalty: {null_penalty}; Threshold: {threshold}")
        self.threshold = threshold
        self.int_cat: dict[str, int] = {
          
            "Start_Date_Day": 0.25,
            "Start_Date_Month": 0.5,
            "Start_Date_Year": 1,
            "End_Date_Day": 0.25,
            "End_Date_Month": 0.5,
            "End_Date_Year": 1,
        }
        self.bool_cat: list[str] = []
         
        self.event_cat: dict[str, int] = {"Main_Event": 1}
        self.list_cat: dict[str, int] = {"Hazards":1}
        self.set_cat:  dict[str, int] ={"Administrative_Areas_GID": 1}
        self.str_cat:dict[str, int] = { "Administrative_Areas_Norm": 1}
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
        

        for si in sys_list:
            scores = []
            skip_instance = False  # Flag to skip further processing for this instance

            for k in gold_instance.keys():
                try:
                    # Check Main Event first
                    if k in self.event_cat:
                        r = self.comp.string(gold_instance[k], si[k])
                        if r is not None and r != 0:
                            scores = [0]  # Set score to 0 for this instance
                            skip_instance = True
                            break  # Exit the field loop for this instance

                        if r == 0:
                            continue  # Skip to the next field
                    # next check the Adminstrative areas 
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

                   

                    # lastly check the time information 
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
   

  
    def find_duplicate_items(self, data_list: list[dict]) -> list[tuple[dict, dict, float]]:
        duplicates = []
        for i in range(len(data_list)):
            for j in range(i+1, len(data_list)):
                sim = self.calc_similarity(data_list[i], [data_list[j]])[0]
                if sim > self.threshold:
                    duplicates.append((data_list[i], data_list[j], sim))
        return duplicates

