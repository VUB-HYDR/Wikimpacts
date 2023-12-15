import normaliser
import itertools

class Comparer():
    """ Comparison module """

    def __init__(self):
        """ Initialisation. """
        self.norm = normaliser.Normaliser()

    def string(self, v, w):
        """ Compare strings. Return 0 if identical, 1 otherwise. """
        if v == None or w == None: return None
        return 1-int(self.norm.string(v) == self.norm.string(w))

    def integer(self, v, w):
        """ Compare integers. Note: assumes non-negative input. """
        if v == None or w == None: return None
        v, w = self.norm.integer(v), self.norm.integer(w)
        return 0.0 if v+w == 0 else abs(v-w)/(v+w)

    def boolean(self, v, w):
        """ Compare booleans. Returns 0 if equal, 0 otherwise. """
        if v == None or w == None: return None
        return int(not (self.norm.boolean(v) == self.norm.boolean(w)))

    def sequence(self, v, w):
        """ Compare sequences. Returns Jaccard distance between sets of elements in sequences.
            Note: ordering is not taken into consideration. """
        if v == None or w == None: return None
        v, w = set(self.norm.sequence(v)), set(self.norm.sequence(w))
        return 1.0-len(v.intersection(w))/len(v.union(w))

    def date(self, v, w):
        """ Compare dates. Returns 0 if identical, 1 othewise. """
        if v == None or w == None: return None
        return 1-int(self.norm.date(v) == self.norm.date(w))

    def all(self, v, w):
        """ Compare all fields. """
        score = {}
        # Strings
        for k in ["Event_Type",
                  "Event_Name",
                  "Insured_Damage_Units",
                  "Total_Damage_Units"]:
            score[k] = self.string(v[k], w[k])
        # Sequences
        for k in ["Location"]:
            score[k] = self.sequence(v[k], w[k])
        # Dates
        for k in ["Single_Date",
                  "Start_Date",
                  "End_Date"]:
            score[k] = self.date(v[k], w[k])
        # Integers
        for k in ["Total_Deaths",
                  "Num_Injured",
                  "Displaced_People",
                  "Num_Homeless",
                  "Total_Affected",
                  "Insured_Damage",
                  "Insured_Damage_Inflation_Adjusted_Year",
                  "Total_Damage",
                  "Total_Damage_Inflation_Adjusted_Year",
                  "Buildings_Damaged"]:
            score[k] = self.integer(v[k], w[k])
        # Booleans
        for k in ["Insured_Damage_Inflation_Adjusted",
                  "Total_Damage_Inflation_Adjusted"]:
            score[k] = self.boolean(v[k], w[k])

        return score

    def averaged(self, v, w):
        """ Average score of all field scores. """
        u = [s for s in self.all(v, w).values() if s != None]
        return sum(u)/len(u)
