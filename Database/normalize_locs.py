import difflib
import re
import pandas as pd


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

        # frequently used literals
        (
            self.city,
            self.county,
            self.state,
            self.country,
            self.region,
            self.subregion,
            self.intermediateregion,
            self.iso,
            self.united_states,
            self.USA_GID,
        ) = (
            "city",
            "county",
            "state",
            "country",
            "Region Name",
            "Sub-region Name",
            "Intermediate Region Name",
            "ISO-alpha3 Code",
            "United States",
            "USA",
        )

        self.unsd_regions, self.unsd_subregions, self.unsd_intermediateregions = (
            self.unsd[self.region].dropna().unique(),
            self.unsd[self.subregion].dropna().unique(),
            self.unsd[self.intermediateregion].dropna().unique(),
        )

        self.us_gadm = self.gadm.loc[self.gadm.COUNTRY == self.united_states]

    def normalize_locations(self, text: str, is_country: bool = False) -> str | None:
        """Queries a geocode service for a location (country or smaller) and returns the top result"""

        if not isinstance(text, str) or not text:
            return
        try:
            text = text.lower().strip()
            # Open Street Map has an issue with "united" countries. "The UK" and "The US" return no results, but "UK" and "US" do.
            query = (
                {
                    self.country: (
                        re.sub(r"(the)", "", text).strip()
                        if text.startswith("the u")
                        else text
                    )
                }
                if is_country
                else text
            )
            l = self.geocode(query, exactly_one=True, namedetails=True)

            us_area = (
                l.raw["display_name"]
                if (
                    l.raw["addresstype"] in [self.county, self.state, self.city]
                    and l.raw["display_name"].split(",")[-1].strip() == "United States"
                )
                else None
            )
            if us_area:
                # retuns US addresses as (area (if present), city (if present), county (if present), state, country)
                return l.raw["display_name"]

            return (
                # return the english name only if a country (due to GADM's format)
                l.raw["namedetails"]["name:en"]
                if (is_country or l.raw["addresstype"] == self.country)
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

    def _get_unsd_region(
        self, area, fuzzy_match_n: int = 1, fuzzy_match_cuttoff: float = 0.8
    ) -> list | None:
        regions = {
            self.region: self.unsd_regions,
            self.subregion: self.unsd_subregions,
            self.intermediateregion: self.unsd_intermediateregions,
        }

        for level, region_list in regions.items():
            if area in region_list:
                return (
                    self.unsd.loc[self.unsd[level] == area][self.iso].unique().tolist()
                )
            else:
                fuzzy_area_match = difflib.get_close_matches(
                    area, region_list, n=fuzzy_match_n, cutoff=fuzzy_match_cuttoff
                )
                if fuzzy_area_match:
                    return (
                        self.unsd.loc[self.unsd[level] == fuzzy_area_match[0]][self.iso]
                        .unique()
                        .tolist()
                    )

    def _get_american_area(self, area: str, country: str = None) -> list | None:
        # TODO: slim down

        areas = []
        if area == self.united_states and not country:
            return [self.USA_GID]

        address = [x.strip() for x in area.split(",")]
        assert address

        if country == self.united_states and address[-1] != self.united_states:
            address.append(country)

        assert address[-1] == self.united_states

        # county level
        if len(address) == 3:
            us_state = address[-2]
            us_county = address[-3]

            areas = (
                self.us_gadm.loc[
                    (self.us_gadm.NAME_1 == us_state)
                    & (self.us_gadm.NAME_2 == us_county)
                ]
                .GID_2.unique()
                .tolist()
            )

            # if not found, clean out surplus names like "county"
            if not areas:
                us_county = re.sub(
                    r"(county)", "", us_county, flags=re.IGNORECASE
                ).strip()
                areas = (
                    self.us_gadm.loc[
                        (self.us_gadm.NAME_1 == us_state)
                        & (self.us_gadm.NAME_2 == us_county)
                    ]
                    .GID_2.unique()
                    .tolist()
                )

        # state level
        elif len(address) == 2:
            us_state = address[-2]

            areas = (
                self.us_gadm.loc[(self.us_gadm.NAME_1 == us_state)]
                .GID_1.unique()
                .tolist()
            )

        # deeper address
        elif len(address) > 3:
            us_state = address[-2]
            us_county = address[-3]

            areas = (
                self.us_gadm.loc[
                    (self.us_gadm.NAME_1 == us_state)
                    & (self.us_gadm.NAME_2 == us_county)
                ]
                .GID_2.unique()
                .tolist()
            )

            # if not found, clean out surplus names like "county"
            if not areas:
                us_county = re.sub(
                    r"(county)", "", us_county, flags=re.IGNORECASE
                ).strip()
                areas = (
                    self.us_gadm.loc[
                        (self.us_gadm.NAME_1 == us_state)
                        & (self.us_gadm.NAME_2 == us_county)
                    ]
                    .GID_2.unique()
                    .tolist()
                )

            areas = [f"{i}:{','.join(address[:-3]).strip()}" for i in areas]

        return areas

    def get_gadm_gid(
        self,
        area: str = None,
        country: str = None,
        row: list = None,
        area_col: str = None,
        country_col: str = None,
    ) -> str:
        if not area and area_col and row:
            area = row[area_col]
        if not country and country_col and row:
            country = row[country_col]

        # find regions in unsd
        unsd_search_output = (
            self._get_unsd_region(area) if area and not country else None
        )
        if unsd_search_output:
            return unsd_search_output

        # limit GADM search to one country
        gadm_df = (
            self.gadm.loc[self.gadm["COUNTRY"] == country] if country else self.gadm
        )

        # handle American States
        us_search_output = (
            self._get_american_area(area, country)
            if country == self.united_states
            or area.split(",")[-1].strip() == self.united_states
            else None
        )
        if us_search_output:
            return us_search_output

        # handle countries
        if country in gadm_df["COUNTRY"].to_list() and not area:
            return gadm_df.loc[gadm_df["COUNTRY"] == country].GID_0.unique().tolist()

        # if trying to get matches in a single country, do fuzzy search
        if country and area:
            unique_area_sets = [
                gadm_df[f"NAME_{i}"].dropna().unique().tolist() for i in range(1, 6)
            ]
            i = 1
            for area_set in unique_area_sets:
                closest_match = difflib.get_close_matches(
                    area, area_set, n=1, cutoff=0.65
                )
                print(closest_match)
                if closest_match:
                    return (
                        gadm_df.loc[gadm_df[f"NAME_{i}"] == closest_match[0]][
                            f"GID_{i}"
                        ]
                        .unique()
                        .tolist()
                    )
                i += 1

        for i in range(1, 6):
            name_col, gid_col = f"NAME_{i}", f"GID_{i}"
            if area in gadm_df[name_col].to_list():
                return gadm_df.loc[gadm_df[name_col] == area][gid_col].unique().tolist()

            # clean out additional parts of a location name (like "county" or "city")
            alt_name = re.sub(r"(county)|(city)", "", area, flags=re.IGNORECASE).strip()
            if alt_name in gadm_df[name_col].to_list():
                return (
                    gadm_df.loc[gadm_df[name_col] == alt_name][gid_col]
                    .unique()
                    .tolist()
                )

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
