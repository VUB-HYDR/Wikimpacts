from geopy.geocoders import Bing


class NormalizeLoc:
    def __init__(
        self,
        geocode: any,
        gadm_path: str,
        unsd_path: str,
    ):
        self.service = geocode
        self.gadm = pd.read_csv(gadm_path, sep=None)
        self.unsd = pd.read_csv(unsd_path, sep=None)

    def normalize_locations(self, text: str, is_country: bool = False) -> str | None:
        """Queries a geocode service for a location (country or smaller) and returns the top result"""
        if not isinstance(text, str) or not text:
            return
        try:
            text = text.lower().strip()
            # Open Street Map has an issue with "united" countries. "The UK" and "The US" return no results, but "UK" and "US" do.
            query = (
                {
                    "country": (
                        text.replace("the ", "") if text.startswith("the u") else text
                    )
                }
                if is_country
                else text
            )
            pprint(query)
            l = self.service(query, exactly_one=True, namedetails=True)

            return (
                # return the english name only if a country (due to GADM's format)
                l.raw["namedetails"]["name:en"]
                if is_country
                else (
                    # return the international name if present (only for sublocations, due to GADM's format)
                    l.raw["namedetails"]["int_name"]
                    if "int_name" in l.raw["namedetails"].keys()
                    else l.raw["namedetails"]["name"]
                )
            )
        except BaseException as err:
            print(
                f"Could not find location {text} (is country? {is_country}). Error message",
                err,
            )
            return

    @staticmethod
    def extract_locations(
        text: str,
    ) -> tuple[list] | None:
        """
        Extracts countries and sublocations from the '|, &' string format
        Example:
        Input: "southern France&France|Spain|Paris&France"
        Output: (['France', 'Spain', 'France'], [['southern France'], [], ['Paris']])
        """
        countries, locations = [], []
        try:
            split_by_pipe = text.split("|")
        except BaseException:
            return
        try:
            if split_by_pipe:
                for s in split_by_pipe:
                    split_by_ampersand = s.split("&")
                    locations_tmp = split_by_ampersand[:-1]
                    locations_tmp = [i.strip() for i in locations_tmp]
                    countries.append(split_by_ampersand[-1].strip())
                    locations.extend([locations_tmp])
            return countries, locations
        except BaseException:
            return

    @staticmethod
    def _debug(response, _print: bool = True):
        if response:
            if _print:
                print(type(response))
            return True
