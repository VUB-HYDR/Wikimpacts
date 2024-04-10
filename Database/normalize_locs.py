from geopy.geocoders import Bing


class NormalizeLoc:
    def __init__(self, service: Bing):
        self.service = service

    def normalize_locations(self, text: str) -> str | None:
        if not isinstance(text, str) or not text:
            return
        try:
            l = self.service.geocode(text, include_country_code=True)
            return l.raw["name"]
        except BaseException:
            return

def extract_locations(
    text: str,
) -> tuple[list] | dict[str:list] | None:

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


def debug(response, _print: bool = False):
    if response:
        if _print: print(type(response))
        return True


if __name__ == "__main__":
    # run an example
    import requests_cache

    requests_cache.install_cache("Database/geopy_cache", filter_fn=debug)

    from dotenv import load_dotenv
    import os

    load_dotenv()
    api_key = os.getenv("BING_MAPS_API_KEY")
    geolocator = Bing(api_key=api_key, user_agent="shorouq.zahra@ri.se")
    norm = NormalizeLoc(geolocator)

    examples = [
        "Papua New Guinea|Queensland & Northern Territory & Australia",
        "Sichuan&Guangdong&Jiangxi&Guangxi&Guizhou&Yunnan&Hong Kong&China",
        "Florida&Outer Banks&Virginia&New England&the United States|London&United Kingdom|Paris&France",
        "Florida&Outer Banks&Virginia&New England&the United States|London&United Kingdom|Paris&France",
        "Florida&Outer Banks&Virginia&New England&the United States|London&United Kingdom|Paris&France",
        "Florida&Outer Banks&Virginia&New England&the United States|London&United Kingdom|Paris&France",
        "Florida&Outer Banks&Virginia&New England&the United States|London&United Kingdom|Paris&France",
        "Florida&Outer Banks&Virginia&New England&the United States|London&United Kingdom|Paris&France",
        # "Florida&Outer Banks&Virginia&New England&the United States",
        # "Russia|Alaska&the United States|Canada|Mexico|United Kingdom|Denmark|Estonia|Finland|Ireland|Latvia|Lithuania|Norway|Sweden",
        # "Hubei&Hunan&Zhejiang&Guizhou&Guangdong&Jiangxi&Guangxi&Fujian&Henan&Shandong&Jiangsu&Anhui&Shanghai&Chongqing&Shanxi&Sichuan&China",
        # "Greece|Cyprus|Israel",
        # "Uttarakhand&Himachal Pradesh&Uttar Pradesh&India|Sudurpashchim Pradesh&Karnali Pradesh&Nepal|Tibet&China",
        # "Interior Division of Sabah&Kota Kinabalu&Penampang&Tuaran&Malaysia",
        # "Windward Islands|Leeward Antilles|Venezuela|Colombia|Hispaniola|Puerto Rico| Cuba|Jamaica|Turks and Caicos Islands|The Bahamas|the United States|Atlantic Canada&Canada",
        # "Hawaii",
        # "Hyōgo Prefecture&Japan",
        # "Leeward Islands|Puerto Rico|Dominican Republic|Lucayan Archipelago|Bermuda|Canada|Saint Pierre and Miquelon|Greenland",
        # "Lesser Antilles|Puerto Rico|New England&the United States|Atlantic Canada&Canada",
        # "Sri Lanka|India",
    ]  #

    for i in examples:
        print(i)
        country, location = extract_locations(i)
        country_norm = [norm.normalize_locations(i, geolocator) for i in country]
        location_norm = [
            [norm.normalize_locations(x, geolocator) for x in i] for i in location
        ]
        print("countries:", country)
        print("NORMALIZED:", country_norm)
        print()

        print("locations:", location)
        print("NORMALIZED:", location_norm)
