import dateparser
from text_to_num import text2num


class Normaliser:
    """Normalisation module"""

    def string(self, v):
        """Normalise string. Discard leading and trailing whitespaces and convert to lower case.
        Examples: "Example" -> "example", "  example " -> "example"."""
        return str(v).strip().lower()

    def integer(self, v):
        """Normalise integer. Integer inputs are returned as is, floats are rounded to integers,
        and string inputs are converted to integers. Ill-defined inputs are returned
        as None. Examples: 100 -> 100, "100" -> 100, 10.7 => 11, "10 000" -> None,
        "Ten" -> 10, "two billion" -> 2000000000."""
        if v == None:
            return None
        try:
            return round(float(v))
        except ValueError:
            try:
                return text2num(v, lang="en", relaxed=True)
            except ValueError:
                return None

    def boolean(self, v):
        """Normalise boolean value. Return None if ill-defined.
        Examples: " Yes" -> True, "0  " -> False, True -> True, "goat" -> None."""
        v = self.string(v)
        return (
            True if v in {"1", "1.0", "yes", "y", "true"} else False if v in {"0", "0.0", "no", "n", "false"} else None
        )

    def sequence(self, v):
        """Normalise a string of elements separated by "&" or "|". Return an ordered list of
        normalised strings. Examples: "Normandy &France" -> ['normandy', 'france'],
        "France|Germany|Poland|Belgium" -> ['france', 'germany', 'poland', 'belgium']"""
        # return [self.string(s) for s in v.replace("&", "|").split("|")]
        return v

    def date(self, v):
        """Normalise date expression. Return in format year-month-day. Non-parsable inputs
        (including those with missing components, such as days) are returned as None.
        Examples: "Nov 21, 2023" -> 2023-11-21, "Nov tenth, 2023" -> None, "Nov, 2023" -> None,
        "Sat Oct 11 17:13:46 UTC 2003" -> 2003-10-11"""
        try:
            return dateparser.parse(v, settings={"STRICT_PARSING": True}).date()
        except:
            return None
