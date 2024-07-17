from Evaluation.normaliser import Normaliser


class Comparer:
    """Comparison module"""

    def __init__(self, null_penalty: bool, target_columns: list[str]):
        """Initialisation."""
        # Penalty score if one field is None, but not the other
        self.null_penalty = null_penalty
        self.norm = Normaliser()
        self.target_columns = target_columns

    def target_col(self, l) -> list:
        """Returns a list of columns if they are in the set of specified target columns"""
        return list(set(l) & set(self.target_columns))

    def string(self, v, w):
        """Compare strings. Return 0 if identical, 1 otherwise."""
        if v == None and w == None:
            return 0
        if v == None and w != None or v != None and w == None:
            return self.null_penalty
        return 1 - int(self.norm.string(v) == self.norm.string(w))

    def integer(self, v, w):
        """Compare integers. Note: assumes non-negative input."""
        v, w = self.norm.integer(v), self.norm.integer(w)

        if v == None and w == None:
            return 0
        if v == None and w != None or v != None and w == None:
            return self.null_penalty
        return 0.0 if v + w == 0 else abs(v - w) / (v + w)

    def boolean(self, v, w):
        """Compare booleans. Returns 0 if equal, 1 otherwise."""
        if v == None and w == None:
            return 0
        if v == None and w != None or v != None and w == None:
            return self.null_penalty
        return int(not (self.norm.boolean(v) == self.norm.boolean(w)))

    def sequence(self, v, w):
        """Compare sequences. Returns Jaccard distance between sets of elements in sequences.
        Note: ordering is not taken into consideration."""
        if v == None and w == None:
            return 0
        if v == None and w != None or v != None and w == None:
            return self.null_penalty
        v, w = set(self.norm.sequence(v)), set(self.norm.sequence(w))
        return 1.0 - len(v.intersection(w)) / len(v.union(w))

    def date(self, v, w):
        """Compare dates. Returns 0 if identical, 1 othewise."""
        if v == None and w == None:
            return 0
        if v == None and w != None or v != None and w == None:
            return self.null_penalty
        return 1 - int(self.norm.date(v) == self.norm.date(w))

    def all(self, v, w):
        """Compare all fields."""
        score = {}
        # Strings
        for k in self.target_col(["Main_Event", "Event_ID", "Event_Name", "Total_Damage_Units"]):
            score[k] = self.string(v[k], w[k])

        # Sequences
        for k in self.target_col(["Country_Norm"]):
            score[k] = self.sequence(v[k], w[k])

        # Dates
        for k in []:
            score[k] = self.date(v[k], w[k])

        # Integers
        for k in self.target_col(
            [
                "Total_Deaths_Min",
                "Total_Deaths_Max",
                "Start_Date_Day",
                "Start_Date_Month",
                "Start_Date_Year",
                "End_Date_Day",
                "End_Date_Month",
                "End_Date_Year",
                "Total_Damage_Min",
                "Total_Damage_Max",
                "Total_Homeless_Min",
                "Total_Homeless_Max",
                # Injuries
                "Total_Injuries_Max",
                "Total_Injuries_Min",
                # Buildings_Damage
                "Total_Buildings_Min",
                "Total_Buildings_Max",
                # Affected
                "Total_Affected_Min",
                "Total_Affected_Max",
                # Homeless
                "Total_Damage_Units",
                "Total_Damage_Inflation_Adjusted",
                "Total_Damage_Inflation_Adjusted_Year",
                # Insured Damage
                "Total_Insured_Damage_Min",
                "Total_Insured_Damage_Max",
                "Total_Insured_Damage_Units",
                "Total_Insured_Damage_Inflation_Adjusted",
                "Total_Insured_Damage_Inflation_Adjusted_Year",
                # Displace
                "Total_Displace_Min",
                "Total_Displace_Max",
            ]
        ):
            score[k] = self.integer(v[k], w[k])

        # Booleans
        for k in self.target_col([]):
            score[k] = self.boolean(v[k], w[k])

        # Return score dictionary after ordering by target columns order
        ordered_score = {k: score[k] for k in self.target_columns}
        return ordered_score

    def averaged(self, v, w):
        """Return fraction of null comparisons (Nones) and mean of remaining scores."""
        u = [s for s in self.all(v, w).values() if s != None]
        return 1.0 - len(u) / len(v), sum(u) / len(u)

    def weighted(self, v, w, weights):
        """Return fraction of null comparisons (Nones) and weighted mean of remaining scores.
        Items with weight 0 are ignored."""
        p = dict([(k, s) for (k, s) in self.all(v, w).items() if weights[k] != 0])
        u = [weights[k] * s for (k, s) in p.items() if s != None]
        return 1.0 - len(u) / len(p) if len(p) != 0 else None, (sum(u) / len(u) if len(u) != 0 else None)

    def relevance(self, vv, ww, weights):
        """Measure how events in vv are represented by events in ww.
        For each event v in vv, find the least different event w in ww.
        Record the difference score between v and w and remove w from ww.
        If there are fewer events in ww than in vv, add null events to ww."""
        # If there are fewer events in ww than in vv, add null events to ww
        ww_padded = ww.copy()
        null_event = dict([(key, None) for key in vv[0].keys()])
        while len(ww_padded) < len(vv):
            ww_padded.append(null_event)
        total_score = 0
        for v in vv:
            # Agreements between v and every event w in ww
            scores = [self.weighted(v, w, weights)[1] for w in ww_padded]
            # Get index of smallest weighted score (i.e., largest agreement)
            min_index = min(range(len(scores)), key=scores.__getitem__)
            # Accumulate min score
            total_score += min(scores)
            # Remove event from ww which had the largest agreement with v
            del ww_padded[min_index]
        # Return mean of total score
        return total_score / len(vv)

    def events(self, annotated, retrieved, weights):
        """Compare two event sets."""
        # Measure to what extent events in "retrieved" are relevant
        precision = self.relevance(retrieved, annotated, weights)
        # Meaure to what extent events in "annotated" are retrieved
        recall = self.relevance(annotated, retrieved, weights)
        return precision, recall
