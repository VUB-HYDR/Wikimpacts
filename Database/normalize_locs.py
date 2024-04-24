import pandas as pd
import us
from pprint import pprint


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

    def get_gadm_gid(self, area: str = None, country: str = None) -> str:
        region, subregion, intermediateregion, iso, united_states = (
            "Region Name",
            "Sub-region Name",
            "Intermediate Region Name",
            "ISO-alpha3 Code",
            "United States",
        )
        if area in self.unsd[region].unique():
            return self.unsd.loc[self.unsd[region] == area][iso].unique().tolist()
        if area in self.unsd[subregion].unique():
            return self.unsd.loc[self.unsd[subregion] == area][iso].unique().tolist()
        if area in self.unsd[intermediateregion].unique():
            return (
                self.unsd.loc[self.unsd[intermediateregion] == area][iso]
                .unique()
                .tolist()
            )

        gadm_df = (
            self.gadm.loc[self.gadm["COUNTRY"] == country] if country else self.gadm
        )

        # handle American States
        us_state = None
        if country == united_states:
            try:
                state = area.split(",")[-1].strip()
                if len(state) == 2:
                    us_state = us.states.lookup(state)
            except:
                us_state = None
        if us_state:
            areas = (
                self.gadm.loc[
                    (self.gadm.COUNTRY == united_states)
                    & (self.gadm.NAME_1 == us_state.name)
                ]["GID_1"]
                .unique()
                .tolist()
            )
            return [f"{i}:{area.split(',')[0].strip()}" for i in areas]

        # handle countries
        if area in gadm_df["COUNTRY"].to_list():
            return gadm_df.loc[gadm_df["COUNTRY"] == area]["GID_0"].unique().tolist()

        # handle rest of GADM
        deepest = []
        for i in range(1, 6):
            name_col, gid_col = f"NAME_{i}", f"GID_{i}"
            if area in gadm_df[name_col].to_list():
                deepest = (
                    gadm_df.loc[gadm_df[name_col] == area][gid_col].unique().tolist()
                )
        return deepest

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
