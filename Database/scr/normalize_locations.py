import difflib
import json
import re
from functools import cache
from time import sleep

import pandas as pd
import pycountry
import requests_cache
from geopy.geocoders import Nominatim

from .log_utils import Logging


class NormalizeLocation:
    def __init__(self, gadm_path: str, unsd_path: str):
        self.geopy_cache_path = "Database/data/geopy_cache"
        requests_cache.install_cache(
            self.geopy_cache_path, allowable_methods=["GET"], allowable_codes=[200], filter_fn=self._rate_limiter
        )
        geolocator = Nominatim(user_agent="wikimpacts - impactdb; beta. Github: VUB-HYDR/Wikimpacts")
        self.geocode = geolocator.geocode
        self.gadm = pd.read_csv(gadm_path, sep=None, engine="python")
        self.unsd = pd.read_csv(unsd_path, sep=None, engine="python")

        for col in self.unsd.columns:
            if "Code" not in col:
                self.unsd[col] = self.unsd[col].apply(lambda s: s.lower() if type(s) == str else s)

        self.logger = Logging.get_logger("normalize_locations", level="INFO")
        self.logger.info("Installed GeoPy cache")
        # frequently used literals
        (
            self.city,
            self.national_park,
            self.protected_area,
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
            "national_park",
            "protected_area",
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

        # See location types at https://wiki.openstreetmap.org/wiki/TMC/Location_Code_List/Location_Types
        self.unwanted_location_types = [
            "commercial",
            "industrial",
            "company",
            "clinic",
            "hospital",
            "residential",
            "retail",
            "university",
            "restaurant",
            "car park",
            "motel",
            "petrol stration with kiosk",
            "petrol station",
            "retail park",
            "exhibition/convention centre",
            "underground parking garage",
            "car park",
            "carpool point",
            "car park area",
            "kiosk with WC",
            "cemetery",
            "church",
        ]

        self.unsd_regions, self.unsd_subregions, self.unsd_intermediateregions = (
            self.unsd[self.region].dropna().unique(),
            self.unsd[self.subregion].dropna().unique(),
            self.unsd[self.intermediateregion].dropna().unique(),
        )

        self.us_gadm = self.gadm.loc[self.gadm.COUNTRY == self.united_states]

        self.cardinals = ["north", "south", "east", "west", "north east", "north west", "south east", "south west"]
        self.cardinals.extend([f"{i}ern" for i in self.cardinals])
        self.cardinals.extend(
            [
                "central",
                "centre",
                "center",
                "downtown",
                "remote",
                "isolated",
                "distant",
                "urban",
                "suburban",
                "regional",
            ]
        )

    def _clean_cardinal_directions(self, area: str) -> tuple[str, list[str]]:
        area = area.split()
        output = [i.strip() for i in area if i.lower().strip() not in self.cardinals]
        cardinals = [i.strip() for i in area if i.lower().strip() in self.cardinals]
        return " ".join(output), " ".join(cardinals) if cardinals else None

    def geocode_api_request(
        self,
        query: str,
        exactly_one: bool,
        namedetails: bool,
        geometry: str,
        extratags: bool,
        country_codes: list[str] | None = None,
    ) -> list:
        try:
            l = self.geocode(
                query=query,
                exactly_one=exactly_one,
                namedetails=namedetails,
                geometry=geometry,
                extratags=extratags,
                country_codes=country_codes,
            )
            return l if l else []
        except BaseException as err:
            self.logger.error(f"API call unsuccessful. Error message: {err}")
            return []

    def normalize_locations(
        self, area: str, is_country: bool = False, in_country: str = None
    ) -> tuple[str | None, str | None, dict | None]:
        """Queries a geocode service for a location (country or smaller) and returns the top result"""
        original_area = area
        try:
            try:
                if area:
                    assert isinstance(area, str), f"Area `{area}` is not a string; type: {type(area)}"
                if re.match(
                    "(country|location|area|adminarea|admin|admin_area|administrative area|administrative_area|none|null)(\s)*(s)*[0-9]*$",
                    area,
                    flags=re.IGNORECASE,
                ):
                    self.logger.error(f"Input `{area}` of type {type(area)} is not a valid area name")
                    return (None, None, None)
                if in_country:
                    assert isinstance(in_country, str), f"Country is not a string: {in_country}"
                assert not (
                    is_country and in_country
                ), f"An area cannot be a country (is_country={is_country}) and in a country (in_country={in_country}) simultaneously"

            except BaseException as err:
                self.logger.error(err)
                return (None, None, None)

            # attempt to find region name in unsd if an area is passed as a country
            unsd_search_output = self._get_unsd_region(area, return_name=True) if area and is_country else None
            if unsd_search_output:
                # TODO: add geojson for unsd regions
                return [unsd_search_output.title(), "UNSD region", None]

            # corner case
            area = "China" if area == "Mainland China" else area
            area = area.lower().strip()
            if "_" in area:
                area = area.replace("_", " ")

            if isinstance(in_country, str):
                in_country = in_country.lower().strip()

            country_codes = None
            location = None

            # Open Street Map has an issue with "united" countries. "The UK" and "The US" return no results, but "UK" and "US" do.
            if is_country:
                query = {self.country: (re.sub(r"(the)", "", area).strip() if area.startswith("the u") else area)}
            elif in_country:
                query = area
                try:
                    country_codes = pycountry.countries.search_fuzzy(in_country)[0].alpha_2
                except BaseException as err:
                    self.logger.debug(
                        f"Could not extract country code. Country {in_country} may be incorrect. Error message {err}"
                    )
            else:
                query = area

            l = self.geocode_api_request(
                query,
                exactly_one=False,
                namedetails=True,
                geometry="geojson",
                extratags=True,
                country_codes=country_codes,
            )

            # if no results are found if the area is_country, attempt again without the country constraint
            if not l and is_country:
                l = self.geocode_api_request(
                    area,
                    exactly_one=False,
                    namedetails=True,
                    geometry="geojson",
                    extratags=True,
                    country_codes=country_codes,
                )

            # if results fail again or no suitable location type is found, attempt removing cardinal directions from the name
            if not l or any([r.raw["type"].lower().strip() in self.unwanted_location_types for r in l]):
                area_no_cardinals, cardinals = self._clean_cardinal_directions(area)
                l = self.geocode_api_request(
                    area_no_cardinals,
                    exactly_one=False,
                    namedetails=True,
                    geometry="geojson",
                    extratags=True,
                    country_codes=country_codes,
                )
            else:
                cardinals = None

            # if results fail again, clean out additional parts of a location name (like "county" or "city")
            if not l:
                alt_name = re.sub(
                    r"(county)|(prefecture)|(district)|(district of)|(city)|(city of)|(region)|(region of)",
                    "",
                    area,
                    flags=re.IGNORECASE,
                ).strip()
                l = self.geocode_api_request(
                    alt_name,
                    exactly_one=False,
                    namedetails=True,
                    geometry="geojson",
                    extratags=True,
                    country_codes=country_codes,
                )

            # if results fail again, get results for each possible segment and sort by rank without country restraints
            if not l:
                l = []
                area_segments = area.split(" ")
                for a in area_segments:
                    l.extend(
                        self.geocode_api_request(
                            a,
                            exactly_one=False,
                            namedetails=True,
                            geometry="geojson",
                            extratags=True,
                        )
                    )
            l = sorted(l, key=lambda x: x.raw["place_rank"], reverse=False)
            for result in l:
                # prefer areas that are a multigon/polygon (aka not "point")
                if result.raw["geojson"]["type"].strip().lower() != "point":
                    # prefer administrative locations
                    if result.raw["type"].lower().strip() == "administrative":
                        location = result
                        break
                    # prefer non-commercial locations (avoid matching shops/stores/offices)
                    elif result.raw["type"].lower().strip() not in self.unwanted_location_types:
                        location = result
                        break
                else:
                    location = None

            # if all matched locations are points and/or commercial, grab the one with the lowest rank
            if not location:
                if l:
                    location = l[0]
                # otherwise, generalize to the country
                elif not l and in_country:
                    l = self.geocode_api_request(
                        {"country": in_country},
                        exactly_one=False,
                        namedetails=True,
                        geometry="geojson",
                        extratags=True,
                    )
                    l = sorted(l, key=lambda x: x.raw["place_rank"], reverse=False)
                    location = l[0]

            us_area = (
                location.raw["display_name"]
                if (
                    location.raw["addresstype"]
                    in [self.county, self.state, self.city, self.national_park, self.protected_area]
                    and location.raw["display_name"].split(",")[-1].strip() == "United States"
                )
                else None
            )

            normalized_area_name = None

            if us_area:
                # retuns US addresses as (area (if present), city (if present), county (if present), state, country)
                normalized_area_name = location.raw["display_name"]
            else:
                # return the english name only if a country (due to GADM's format)
                if is_country or location.raw["addresstype"] == self.country:
                    if "name:en" in location.raw["namedetails"].keys():
                        normalized_area_name = location.raw["namedetails"]["name:en"]
                    elif "name" in location.raw["namedetails"].keys():
                        normalized_area_name = location.raw["namedetails"]["name"]
                # return the international name or wikipedia title if present (only for sublocations, due to GADM's format)
                elif "int_name" in location.raw["namedetails"].keys():
                    normalized_area_name = location.raw["namedetails"]["int_name"]
                elif "name" in location.raw["namedetails"].keys():
                    normalized_area_name = location.raw["namedetails"]["name"]
                elif (
                    "wikipedia" in location.raw["extratags"].keys() and "en:" in location.raw["extratags"]["wikipedia"]
                ):
                    normalized_area_name = location.raw["extratags"]["wikipedia"].replace("en:", "").strip()
                else:
                    normalized_area_name = (
                        location.raw["namedetails"]["name"]
                        if location.raw["namedetails"]["name"] not in [None, "None", "none"]
                        else location.raw["display_name"]
                    )

            # if the location had any cardinal directions attached, add them here
            # only if the location is smaller than a country
            if cardinals and not is_country:
                normalized_area_name = f"{normalized_area_name}:<{cardinals}>"
            geojson = json.dumps(location.raw["geojson"]) if isinstance(location.raw["geojson"], dict) else None
            return (normalized_area_name, f'{location.raw["type"]}:{location.raw["addresstype"]}', geojson)

        except BaseException as err:
            self.logger.error(
                f"Could not find location {area}; is_country: {is_country}; in_country: {in_country}. Error message: {err}."
            )
            # return un-normalized area name
            return (original_area, None, None)

    def _get_unsd_region(
        self, area, fuzzy_match_n: int = 1, fuzzy_match_cuttoff: float = 0.8, return_name: bool = False
    ) -> str | list | None:
        regions = {
            self.region: self.unsd_regions,
            self.subregion: self.unsd_subregions,
            self.intermediateregion: self.unsd_intermediateregions,
        }

        for level, region_list in regions.items():
            if area in region_list:
                return area if return_name else self.unsd.loc[self.unsd[level] == area][self.iso].unique().tolist()
            else:
                fuzzy_area_match = difflib.get_close_matches(
                    area, region_list, n=fuzzy_match_n, cutoff=fuzzy_match_cuttoff
                )
                if fuzzy_area_match:
                    return (
                        fuzzy_area_match[0]
                        if return_name
                        else self.unsd.loc[self.unsd[level] == fuzzy_area_match[0]][self.iso].unique().tolist()
                    )
        return None

    @cache
    def _get_american_area(self, area: str) -> list | None:
        # TODO: slim down
        areas = []
        if not area:
            return None

        if area == self.united_states:
            return [self.USA_GID]

        address = [x.strip() for x in area.split(",")] if area else [x.strip() for x in area.split(",")]

        # remove postal codes from the address list (common on OSM)
        address = [i for i in address if not re.match(r"^\d{5}(?:[-\s]\d{4})?$", i)]

        if address[-1] != self.united_states:
            address.append(self.united_states)

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

            # if not found, generalize to the state
            if not areas:
                areas = self.us_gadm.loc[(self.us_gadm.NAME_1 == us_state)].GID_1.unique().tolist()

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

        return areas if areas else None

    @cache
    def get_gadm_gid(
        self,
        area: str | None = None,
        country: str | None = None,
    ) -> list:
        # remove cardinals when getting gid
        # TODO: this should probably be handled by something other than symbols in strings, fix
        country = country.split(":")[0] if country and ":" in country else country
        area = area.split(":")[0] if area and ":" in area else area
        country_cols = ["COUNTRY", "NAME_0", "VARNAME_0"]

        # find regions in unsd
        unsd_loc = area if area and not country else country
        unsd_search_output = self._get_unsd_region(unsd_loc, return_name=False)
        if unsd_search_output:
            return unsd_search_output

        # find US-areas: country, states, and counties
        us_search: str | None = None
        if country and not area:
            us_search = country
        elif area and not country:
            us_search = area
        elif area and country:
            us_search = (
                area
                if (self.united_states in country and self.united_states in area)
                else (country if not area else (f"{area}, {country}" if country and area else None))
            )

        us_search_output = self._get_american_area(us_search)
        if us_search_output:
            return us_search_output

        # limit GADM search to one country
        gadm_df = pd.DataFrame()
        for col in country_cols:
            if country in self.gadm[col].unique().tolist():  # and not area:
                gadm_df = self.gadm.loc[self.gadm[col] == country]
                if gadm_df.shape[0] != 0:
                    break

        gadm_df = self.gadm if gadm_df.shape[0] == 0 else gadm_df

        # handle countries, match in order by country column, name at level 0, or alternative names at level 0
        for col in country_cols:
            if country in gadm_df[col].unique().tolist() and not area:
                return gadm_df.loc[gadm_df[col] == country].GID_0.unique().tolist()

        # if trying to get matches in a single country, do fuzzy search
        if country and area:
            unique_area_sets = [gadm_df[f"NAME_{l}"].dropna().unique().tolist() for l in range(1, 6)]
            for cutoff in [0.75, 0.70]:
                level = 1
                for area_set in unique_area_sets:
                    closest_match = difflib.get_close_matches(area, area_set, n=1, cutoff=cutoff)
                    if closest_match:
                        return (
                            gadm_df.loc[gadm_df[f"NAME_{level}"] == closest_match[0]][f"GID_{level}"].unique().tolist()
                        )
                    level += 1

        area = country if (country and not area) else area
        for level in range(1, 6):
            name_col, gid_col = f"NAME_{level}", f"GID_{level}"
            if area in gadm_df[name_col].to_list():
                return gadm_df.loc[gadm_df[name_col] == area][gid_col].unique().tolist()

            # clean out additional parts of a location name (like "county" or "city")
            if isinstance(area, str):
                alt_name = re.sub(
                    r"(county)|(city)|(prefecture)|(district)|(city of)|(region)", "", area, flags=re.IGNORECASE
                ).strip()
                if alt_name in gadm_df[name_col].to_list():
                    return gadm_df.loc[gadm_df[name_col] == alt_name][gid_col].unique().tolist()

        for level in range(1, 5):
            varname_col, gid_col = f"VARNAME_{level}", f"GID_{level}"
            varnames_list = [x for x in gadm_df[varname_col].to_list() if isinstance(x, str)]
            varnames_list = list(set(varnames_list))
            varnames_list = [x.split("|") for x in varnames_list]
            for varnames in varnames_list:
                if area in varnames:
                    return (
                        gadm_df.loc[
                            gadm_df[varname_col].apply(lambda x: True if isinstance(x, str) and area in x else False)
                        ][gid_col]
                        .unique()
                        .tolist()
                    )
        return []

    def get_gid_0(self, gid: str) -> str | None:
        """Returns a country name by GID_0"""
        try:
            assert len(gid) == 3
            gid_0 = list(set(self.gadm.loc[self.gadm["GID_0"] == gid]["NAME_0"]))
            assert len(gid_0) == 1
            return gid_0[0]
        except:
            return None

    @staticmethod
    def extract_locations(
        text: str,
    ) -> tuple[list[str]] | tuple[list, list]:
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
            return [], []
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
            return [], []

    def _rate_limiter(
        self,
        response,
    ):
        self.logger.debug(type(response))
        if type(response) == requests_cache.models.response.CachedResponse:
            self.logger.debug("Response cached!")
        else:
            self.logger.debug(f"Ratelimiting by 1 second. Response type: {type(response)}")
            sleep(1)
        return True
