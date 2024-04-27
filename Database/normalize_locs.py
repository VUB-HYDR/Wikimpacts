import difflib
import re

import pandas as pd
import us
import difflib
import pprint
import re


class NormalizeLoc:
    def __init__(
        self,
        geocode: any,
        gadm_path: str,
        unsd_path: str,
    ):
        self.geocode = geocode
        self.gadm = pd.read_csv(gadm_path, sep=None, engine="python")
        self.unsd = pd.read_csv(unsd_path, sep=None, engine="python")

        # unsd specific variables
        self.region, self.subregion, self.intermediateregion, self.iso, self.united_states = (
            "Region Name",
            "Sub-region Name",
            "Intermediate Region Name",
            "ISO-alpha3 Code",
            "United States",
        )

        self.unsd_regions, self.unsd_subregions, self.unsd_intermediateregions = (
            self.unsd[self.region].dropna().unique(),
            self.unsd[self.subregion].dropna().unique(),
            self.unsd[self.intermediateregion].dropna().unique(),
        )

    def normalize_locations(self, text: str, is_country: bool = False) -> str | None:
        """Queries a geocode service for a location (country or smaller) and returns the top result"""
        if not isinstance(text, str) or not text:
            return
        try:
            text = text.lower().strip()
            # Open Street Map has an issue with "united" countries. "The UK" and "The US" return no results, but "UK" and "US" do.
            query = (
                {
                    "country": 
                    (
                        re.sub(r"(the)", "", text).strip() if text.startswith("the u") else text
                    )
                }
                if is_country
                else text
            )
            l = self.geocode(query, exactly_one=True, namedetails=True)
            # print(l)
            # pprint.pprint(l.raw)

            return (
                # return the english name only if a country (due to GADM's format)
                l.raw["namedetails"]["name:en"]
                if (is_country or l.raw["addresstype"] == "country")
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

    def _get_unsd_region(self, area, fuzzy_match_n: int = 1, fuzzy_match_cuttoff: float = 0.8) -> list | None:
        if area in self.unsd_regions:
            return self.unsd.loc[self.unsd[self.region] == area][self.iso].unique().tolist()
        else:
            fuzzy_area_match = difflib.get_close_matches(
                area, self.unsd_regions, n=fuzzy_match_n, cutoff=fuzzy_match_cuttoff
            )
            if fuzzy_area_match:
                return self.unsd.loc[self.unsd[self.region] == fuzzy_area_match[0]][self.iso].unique().tolist()

        if area in self.unsd_subregions:
            return self.unsd.loc[self.unsd[self.subregion] == area][self.iso].unique().tolist()
        else:
            fuzzy_area_match = difflib.get_close_matches(
                area, self.unsd_subregions, n=fuzzy_match_n, cutoff=fuzzy_match_cuttoff
            )
            if fuzzy_area_match:
                return self.unsd.loc[self.unsd[self.subregion] == fuzzy_area_match[0]][self.iso].unique().tolist()

        if area in self.unsd_intermediateregions:
            return self.unsd.loc[self.unsd[self.intermediateregion] == area][self.iso].unique().tolist()
        else:
            fuzzy_area_match = difflib.get_close_matches(
                area, self.unsd_intermediateregions, n=fuzzy_match_n, cutoff=fuzzy_match_cuttoff
            )
            if fuzzy_area_match:
                return (
                    self.unsd.loc[self.unsd[self.intermediateregion] == fuzzy_area_match[0]][self.iso].unique().tolist()
                )

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
        if country in gadm_df["COUNTRY"].to_list() and not area:
            return gadm_df.loc[gadm_df["COUNTRY"] == country]["GID_0"].unique().tolist()

        # if trying to get matches in a single country, do fuzzy search 
        if country and area:
            unique_area_sets = [
                gadm_df[f"NAME_{i}"].dropna().unique().tolist()
                for i in range(1, 6)
            ]
            i = 1
            for area_set in unique_area_sets:
                closest_match = difflib.get_close_matches(area, area_set, n=1, cutoff=0.65)
                print(closest_match)
                if closest_match: return gadm_df.loc[gadm_df[f"NAME_{i}"] == closest_match[0]][f"GID_{i}"].unique().tolist()
                i += 1

        # handle rest by getting the deepest area GADM (TODO: maybe it should be the largest instead)
        #deepest = []
        for i in range(1, 6):
            name_col, gid_col = f"NAME_{i}", f"GID_{i}"
            if area in gadm_df[name_col].to_list():
                return gadm_df.loc[gadm_df[name_col] == area][gid_col].unique().tolist()
            
            # clean out additional parts of a location name (like "county" or "city")
            alt_name = re.sub(r"(county)|(city)", "", area, flags=re.IGNORECASE).strip()
            if alt_name in gadm_df[name_col].to_list():
                return gadm_df.loc[gadm_df[name_col] == alt_name][gid_col].unique().tolist()
                
                #deepest = (
                #    gadm_df.loc[gadm_df[name_col] == area][gid_col].unique().tolist()
                #)
                #print(deepest)
        #return deepest

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
