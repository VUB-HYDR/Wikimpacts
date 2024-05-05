import difflib
import json
import re

import pandas as pd
import pycountry
import requests_cache
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

from .normalize_utils import NormalizeUtils


class NormalizeLocation:
    def __init__(
        self,
        gadm_path: str,
        unsd_path: str,
    ):
        requests_cache.install_cache("Database/data/geopy_cache", filter_fn=self._debug)

        geolocator = Nominatim(user_agent="wikimpacts - impactdb; beta. Github: VUB-HYDR/Wikimpacts")
        self.geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        self.gadm = pd.read_csv(gadm_path, sep=None, engine="python")
        self.unsd = pd.read_csv(unsd_path, sep=None, engine="python")
        self.logger = NormalizeUtils.get_logger("normalize_locations")

        self.logger.info("Installed GeoPy cache")
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

    def uninstall_cache():
        requests_cache.uninstall_cache()

    def normalize_locations(
        self, area: str, is_country: bool = False, in_country: str = None
    ) -> tuple[str, str, dict] | None:
        """Queries a geocode service for a location (country or smaller) and returns the top result"""

        # print(area, type(area), "is_country", is_country, "in_country", in_country)
        try:
            try:
                assert isinstance(area, str), f"Area is not a string {area}"
            except BaseException as err:
                self.logger.error(err)
                return (None, None, None)
            try:
                assert not (
                    is_country and in_country
                ), f"An area cannot be a country (is_country={is_country}) and in a country (in_country={in_country}) simultaneously"
            except BaseException as err:
                self.logger.error(err)
                return (None, None, None)

            area = area.lower().strip()
            if isinstance(in_country, str):
                in_country = in_country.lower().strip()

            country_codes = None
            # Open Street Map has an issue with "united" countries. "The UK" and "The US" return no results, but "UK" and "US" do.

            if is_country:
                query = {self.country: (re.sub(r"(the)", "", area).strip() if area.startswith("the u") else area)}
            elif in_country:
                query = area
                country_codes = pycountry.countries.search_fuzzy(in_country)[0].alpha_2

            else:
                query = area

            l = self.geocode(
                query,
                exactly_one=False,
                namedetails=True,
                geometry="geojson",
                country_codes=country_codes,
            )
            location = None
            l = sorted(l, key=lambda x: x.raw["importance"], reverse=True)

            for result in l:
                # prefer areas that are a multigon/polygon (aka not "point")
                if result.raw["geojson"]["type"].strip().lower() != "point":
                    # prefer administrative locations
                    if result.raw["type"].lower().strip() == "administrative":
                        location = result
                        break
                    # prefer non-commercial locations (avoid matching shops/stores/offices)
                    elif result.raw["type"].lower().strip() not in ["commercial", "industrial", "company"]:
                        location = result
                        break
                else:
                    location = None

            # if all matched locations are points and/or commercial, grab the one with the highest importance
            if location is None:
                location = l[0]

            us_area = (
                location.raw["display_name"]
                if (
                    location.raw["addresstype"] in [self.county, self.state, self.city]
                    and location.raw["display_name"].split(",")[-1].strip() == "United States"
                )
                else None
            )
            if us_area:
                # retuns US addresses as (area (if present), city (if present), county (if present), state, country)
                normalized_area_name = location.raw["display_name"]
            else:
                # return the english name only if a country (due to GADM's format)
                normalized_area_name = (
                    location.raw["namedetails"]["name:en"]
                    if (is_country or location.raw["addresstype"] == self.country)
                    else (
                        # return the international name if present (only for sublocations, due to GADM's format)
                        location.raw["namedetails"]["int_name"]
                        if "int_name" in location.raw["namedetails"].keys()
                        else (
                            location.raw["namedetails"]["name"]
                            if location.raw["namedetails"]["name"] not in [None, "None", "none"]
                            else location.raw["display_name"]
                        )
                    )
                )
            geojson = json.dumps(location.raw["geojson"]) if isinstance(location.raw["geojson"], dict) else None

            return (normalized_area_name, location.raw["type"], geojson)
        except BaseException as err:
            self.logger.error(
                f"Could not find location {area} (is country? {is_country}; in_country {in_country}). Error message {err}"
            )
            return (None, None, None)

    def _get_unsd_region(self, area, fuzzy_match_n: int = 1, fuzzy_match_cuttoff: float = 0.8) -> list | None:
        regions = {
            self.region: self.unsd_regions,
            self.subregion: self.unsd_subregions,
            self.intermediateregion: self.unsd_intermediateregions,
        }

        for level, region_list in regions.items():
            if area in region_list:
                return self.unsd.loc[self.unsd[level] == area][self.iso].unique().tolist()
            else:
                fuzzy_area_match = difflib.get_close_matches(
                    area, region_list, n=fuzzy_match_n, cutoff=fuzzy_match_cuttoff
                )
                if fuzzy_area_match:
                    return self.unsd.loc[self.unsd[level] == fuzzy_area_match[0]][self.iso].unique().tolist()

    def _get_american_area(self, area: str, country: str = None) -> list | None:
        # TODO: slim down
        areas = []
        if not area:
            return None

        if area == self.united_states and not country:
            return [self.USA_GID]

        address = [x.strip() for x in area.split(",")] if area else [x.strip() for x in country.split(",")]

        if country == self.united_states and address[-1] != self.united_states:
            address.append(country)

        assert address[-1] == self.united_states

        # county level
        if len(address) == 3:
            us_state = address[-2]
            us_county = address[-3]

            areas = (
                self.us_gadm.loc[(self.us_gadm.NAME_1 == us_state) & (self.us_gadm.NAME_2 == us_county)]
                .GID_2.unique()
                .tolist()
            )

            # if not found, clean out surplus names like "county"
            if not areas:
                us_county = re.sub(r"(county)", "", us_county, flags=re.IGNORECASE).strip()
                areas = (
                    self.us_gadm.loc[(self.us_gadm.NAME_1 == us_state) & (self.us_gadm.NAME_2 == us_county)]
                    .GID_2.unique()
                    .tolist()
                )

        # state level
        elif len(address) == 2:
            us_state = address[-2]

            areas = self.us_gadm.loc[(self.us_gadm.NAME_1 == us_state)].GID_1.unique().tolist()

        # deeper address
        elif len(address) > 3:
            us_state = address[-2]
            us_county = address[-3]

            areas = (
                self.us_gadm.loc[(self.us_gadm.NAME_1 == us_state) & (self.us_gadm.NAME_2 == us_county)]
                .GID_2.unique()
                .tolist()
            )

            # if not found, clean out surplus names like "county"
            if not areas:
                us_county = re.sub(r"(county)", "", us_county, flags=re.IGNORECASE).strip()
                areas = (
                    self.us_gadm.loc[(self.us_gadm.NAME_1 == us_state) & (self.us_gadm.NAME_2 == us_county)]
                    .GID_2.unique()
                    .tolist()
                )

            areas = [f"{i}:{','.join(address[:-3]).strip()}" for i in areas]

        return areas

    def get_gadm_gid(
        self,
        area: str = None,
        country: str = None,
    ) -> str:
        # find regions in unsd
        unsd_search_output = self._get_unsd_region(area) if area and not country else None
        if unsd_search_output:
            return unsd_search_output

        # limit GADM search to one country
        gadm_df = self.gadm.loc[self.gadm["COUNTRY"] == country] if country else self.gadm

        # handle American States
        us_address_split = area.split(",")[-1].strip() if area else None
        us_search_output = (
            self._get_american_area(area, country)
            if area and (country == self.united_states or us_address_split == self.united_states)
            else None
        )
        if us_search_output:
            return us_search_output

        # handle countries
        if country in gadm_df["COUNTRY"].to_list() and not area:
            return gadm_df.loc[gadm_df["COUNTRY"] == country].GID_0.unique().tolist()

        # if trying to get matches in a single country, do fuzzy search
        if country and area:
            unique_area_sets = [gadm_df[f"NAME_{l}"].dropna().unique().tolist() for l in range(1, 6)]
            level = 1
            for area_set in unique_area_sets:
                closest_match = difflib.get_close_matches(area, area_set, n=1, cutoff=0.65)
                if closest_match:
                    return gadm_df.loc[gadm_df[f"NAME_{level}"] == closest_match[0]][f"GID_{level}"].unique().tolist()
                level += 1

        area = country if (country and not area) else area
        for level in range(1, 6):
            name_col, gid_col = f"NAME_{level}", f"GID_{level}"
            if area in gadm_df[name_col].to_list():
                return gadm_df.loc[gadm_df[name_col] == area][gid_col].unique().tolist()

            # clean out additional parts of a location name (like "county" or "city")
            alt_name = re.sub(r"(county)|(city)", "", area, flags=re.IGNORECASE).strip()
            if alt_name in gadm_df[name_col].to_list():
                return gadm_df.loc[gadm_df[name_col] == alt_name][gid_col].unique().tolist()

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

    def _debug(self, response):
        self.logger.debug(type(response))
        return True
