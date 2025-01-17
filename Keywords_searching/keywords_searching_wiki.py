import argparse
import pathlib

import pandas as pd
import requests
from bs4 import BeautifulSoup

from Database.scr.normalize_utils import Logging

if __name__ == "__main__":
    logger = Logging.get_logger("keywords_searching")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        help="The name of the output file",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
        help="The directory where the output will land (as .csv)",
        type=str,
    )
    args = parser.parse_args()
    logger.info(f"Passed args: {args}")

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    # Define the keyphrases
    keyphrases_drought = {
        "keyphrases": [
            "drought",
            "droughts",
            "dryness",
            "dry spell",
            "dry spells",
            "rain scarcity",
            "rain scarcities",
            "rainfall deficit",
            "rainfall deficits",
            "water stress",
            "water shortage",
            "water shortages",
            "water insecurity",
            "water insecurities",
            "limited water availability",
            "limited water availabilities",
            "scarce water resources",
            "groundwater depletion",
            "groundwater depletions",
            "reservoir depletion",
            "reservoir depletions",
        ]
    }

    keyphrases_storm = {
        "keyphrases": [
            "windstorm",
            "windstorms",
            "storm",
            "storms",
            "cyclone",
            "cyclones",
            "typhoon",
            "typhoons",
            "hurricane",
            "hurricanes",
            "blizzard",
            "strong winds",
            "low pressure",
            "gale",
            "gales",
            "wind gust",
            "wind gusts",
            "tornado",
            "tornadoes",
            "wind",
            "winds",
            "lighting",
            "lightings",
            "thunderstorm",
            "thunderstorms",
            "hail",
            "hails",
        ]
    }

    keyphrases_rainfall = {
        "keyphrases": [
            "extreme rain",
            "extreme rains",
            "heavy rain",
            "heavy rains",
            "hard rain",
            "hard rains",
            "torrential rain",
            "torrential rains",
            "extreme precipitation",
            "extreme precipitations",
            "heavy precipitation",
            "heavy precipitations",
            "torrential precipitation",
            "torrential precipitations",
            "cloudburst",
            "cloudbursts",
        ]
    }

    keyphrases_heatwave = {
        "keyphrases": [
            "heatwave",
            "heatwaves",
            "heat wave",
            "heat waves",
            "extreme heat",
            "hot weather",
            "high temperature",
            "high temperatures",
        ]
    }

    keyphrases_flood = {
        "keyphrases": [
            "floodwater",
            "floodwaters",
            "flood",
            "floods",
            "inundation",
            "inundations",
            "storm surge",
            "storm surges",
            "storm tide",
            "storm tides",
        ]
    }

    keyphrases_wildfire = {
        "keyphrases": [
            "wildfire",
            "forest fire",
            "bushfire",
            "wildland fire",
            "rural fire",
            "desert fire",
            "grass fire",
            "hill fire",
            "peat fire",
            "prairie fire",
            "vegetation fire",
            "veld fire",
        ]
    }

    keyphrases_coldwave = {
        "keyphrases": [
            "cold wave",
            "cold waves",
            "coldwave",
            "coldwaves",
            "cold snap",
            "cold spell",
            "Arctic Snap",
            "low temperature",
            "low temperatures",
            "extreme cold",
            "cold weather",
        ]
    }

    # Aggregate the keyphrases into a dictionary
    keywords = {
        "flood": keyphrases_flood["keyphrases"],
        "wildfire": keyphrases_wildfire["keyphrases"],
        "storm": keyphrases_storm["keyphrases"],
        "drought": keyphrases_drought["keyphrases"],
        "heatwave": keyphrases_heatwave["keyphrases"],
        "rainfall": keyphrases_rainfall["keyphrases"],
        "coldwave": keyphrases_coldwave["keyphrases"],
    }

    # Convert the dictionary to a DataFrame for better visualization and export
    df_keywords = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in keywords.items()]))

    keywords_urls = {}
    for column in df_keywords.columns:
        for keyword in df_keywords[column]:
            if keyword is not None and keyword not in keywords_urls:
                # Initialize an empty list for each unique keyword
                keywords_urls[keyword] = []
                # Create the search URL
                # html = f"https://en.wikipedia.org/w/index.php?title=Special:Search&limit=5000&offset=0&ns0=1&search=intitle%3A{keyword}&advancedSearch-current={%22fields%22:{%22intitle%22:%22{keyword}%22}}"
                html = f"https://en.wikipedia.org/w/index.php?title=Special:Search&limit=5000&offset=0&ns0=1&search=intitle%3A{keyword}&advancedSearch-current={{%22fields%22:{{%22intitle%22:%22{keyword}%22}}}}"

                # Make the GET request to Wikipedia
                resp = requests.get(html)
                resp.encoding = "utf-8"

                # Parse the response content with BeautifulSoup
                bs = BeautifulSoup(resp.text, "html.parser")

                # Find all the search result headings
                for news in bs.select("div.mw-search-result-heading"):
                    # Construct the URL for the Wikipedia page from the search result
                    url = "https://en.wikipedia.org" + news.select("a")[0]["href"]

                    # Append the URL to the list in the dictionary for the keyword
                    keywords_urls[keyword].append(url)

    # Create a list of dictionaries
    keyword_list = []
    for keyword, urls in keywords_urls.items():
        for url in urls:
            keyword_list.append({"keyword": keyword, "url": url})

    # Find the maximum length of the lists in the dictionary
    max_length = max(len(lst) for lst in keywords_urls.values())

    # Pad each list in the dictionary to have the same length
    for keyword, urls in keywords_urls.items():
        if len(urls) < max_length:
            keywords_urls[keyword].extend([None] * (max_length - len(urls)))

    # Create a DataFrame for it
    keywords_urls_df = pd.DataFrame(keywords_urls)
    # Initialize an empty DataFrame with columns 'Keyword' and 'URL'
    consolidated_urls_df = pd.DataFrame(columns=["Keyword", "URL"])

    for keyword in keywords_urls_df.columns:
        # Extract the column as a Series, dropping NA values which represent empty cells
        urls = keywords_urls_df[keyword].dropna()
        # Create a temporary DataFrame for the current keyword
        temp_df = pd.DataFrame({"Keyword": keyword, "URL": urls})
        # Append the temporary DataFrame to the consolidated DataFrame
        consolidated_urls_df = pd.concat([consolidated_urls_df, temp_df], ignore_index=True)
    # Remove duplicate URLs, keeping the first occurrence of each URL
    consolidated_urls_df_unique = consolidated_urls_df.drop_duplicates(subset="URL", keep="first")
    logger = Logging.get_logger("save the result")
    consolidated_urls_df_unique.to_csv(f"{args.output_dir}/{args.filename}")
