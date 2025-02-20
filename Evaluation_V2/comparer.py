from Evaluation_V2.normaliser import Normaliser
import numpy as np
import pandas as pd



class Comparer:
    """Comparison module"""

    def __init__(self, null_penalty: bool, target_columns: list[str]):
        """Initialisation."""
        # Penalty score if one field is None, but not the other
        self.null_penalty = null_penalty
        self.norm = Normaliser()
        self.target_columns = target_columns

        # Strings
        string_cols = [
            "Main_Event",
            "Event_ID",
            "Administrative_Area_Norm",
            "Country_Norm",
            "Location_Norm",
            "Event_Name",
        ]
        string_cols.extend([x for x in self.target_columns if "_Unit" in x])
        self.string_columns: list = self.target_col(string_cols)

        # Sequences
        self.sequence_columns: list = self.target_col(
            ["Administrative_Areas_Norm", "Locations_Norm","Event_Names", "Hazards","Administrative_Area_GID"]
        )

        # GID in L3 
        self.GID_columns: list = self.target_col(
          [ "Locations_GID"])

        # Dates
        self.date_columns: list = self.target_col([])

        # Integers
        # Dates and all _Min/_Max values for the numerical and monetary impact types and all inflation adjustment years
        self.integer_columns: list = self.target_col(
            [
                k
                for k in [
                    x
                    for x in self.target_columns
                    if "_Date_" in x
                    or x.endswith("_Min")
                    or x.endswith("_Max")
                    or x.endswith("_Inflation_Adjusted_Year")
                ]
            ]
        )

        # Booleans
        self.boolean_columns: list = [
            k for k in self.target_col([x for x in self.target_columns if x.endswith("_Inflation_Adjusted")])
        ]

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
 

    def flatten_list(self, nest_list):
        """Flatten nested lists, ignoring NaN values and empty lists."""
        if nest_list is  None:
           return [] 
        # Check if the input is a string-like list and convert it to a list
        if isinstance(nest_list, str):
            try:
                nest_list = eval(nest_list)
            except (SyntaxError, NameError):
                return []  # Re
        flattened_list = []
        
        for sublist in nest_list:
            if isinstance(sublist, (list, tuple)):  # Check if sublist is a list or tuple
                for item in sublist:
                    if pd.notna(item):  # Ensure item is not NaN
                        flattened_list.append(item)
            elif pd.notna(sublist):  # Handle the case where gid_list contains direct NaN values
                flattened_list.append(sublist)
        
        return flattened_list

    def sequence(self, v, w):
        """Compare sequences. Returns Jaccard distance between sets of elements in sequences.
        Note: ordering is not taken into consideration."""
        if v == None and w == None:
            return 0
        if v == None and w != None or v != None and w == None:
            return self.null_penalty
        v = set(self.flatten_list(v))
        w = set(self.flatten_list(w))

        union_len = len(v.union(w))
        if union_len == 0:
            return 0.0
        return 1.0 - len(v.intersection(w)) / union_len

    
    def compare_gid_lists(self, gid_list_1, gid_list_2):
        """Compare two lists of GIDs from the same country, considering exact matches, hierarchy, and length differences."""

        # Convert lists to sets to identify exact matches
        # Flatten lists to ensure we work with simple lists of strings
        gid_list_1 = self.flatten_list(gid_list_1)
        gid_list_2 = self.flatten_list(gid_list_2)
        set1, set2 = set(gid_list_1), set(gid_list_2)


        # Remove exact matches (score 0)
        common_matches = set1.intersection(set2)
        set1 -= common_matches
        set2 -= common_matches

        # If all elements matched, return 0
        if not set1 and not set2:
            return 0

        score = 0.0
        comparisons = 0

        # Compare remaining GIDs using hierarchical matching
        for g1 in set1:
            best_match_score = 1.0  # Start with worst score
            for g2 in set2:
                score_candidate = self.score_at_level(g1, g2)
                best_match_score = min(best_match_score, score_candidate)  # Take the best match

            score += best_match_score  # Add best match score to total
            comparisons += 1  # Track comparisons

        # Penalty for length difference: remaining unmatched elements in the longer list
        length_diff = abs(len(gid_list_1) - len(gid_list_2))
        length_penalty = length_diff * 0.001  # Each extra unmatched element adds a small penalty

        # Normalize the score based on comparisons and add length penalty
        return ((score + length_penalty)/ max(comparisons, 1)) 


    def score_at_level(self, g1, g2):
        """Return score based on the hierarchical match level."""
        if g1 == g2:
            return 0  # Perfect match
        g1, g2 = str(g1), str(g2)
        # Split the GIDs into components
        g1_parts = g1.split(".")
        g2_parts = g2.split(".")

        # Find the number of matching levels
        matching_levels = 0
        for p1, p2 in zip(g1_parts, g2_parts):
            if p1 == p2:
                matching_levels += 1
            else:
                break  # Stop at the first mismatch

        total_levels = max(len(g1_parts), len(g2_parts))

        # Calculate the mismatch penalty based on depth difference
        depth_difference = abs(len(g1_parts) - len(g2_parts))
        
        # More shared levels = lower penalty
        similarity_ratio = matching_levels / total_levels
        
        # Adjusted penalty based on depth difference
        penalty = depth_difference * 0.0001  # Each level difference adds 0.001 to the score

        # Final score: 1 - similarity ratio with penalty applied
        return 1 - (similarity_ratio * (1 - penalty))



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
        for k in self.string_columns:
            score[k] = self.string(v[k], w[k])

        # Sequences
        for k in self.sequence_columns:
            score[k] = self.sequence(v[k], w[k])

        # for GID
        for k in self.GID_columns:
            score[k]=self.compare_gid_lists(v[k], w[k])

        # Dates
        for k in self.date_columns:
            score[k] = self.date(v[k], w[k])

        # Integers
        # Dates and all _Min/_Max values for the numerical and monetary impact types and all inflation adjustment years
        for k in self.integer_columns:
            score[k] = self.integer(v[k], w[k])

        # Booleans
        for k in self.boolean_columns:
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
