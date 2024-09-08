import argparse
import json
import pathlib

import pandas as pd
import requests
import tqdm
from bs4 import BeautifulSoup
from unidecode import unidecode

from Database.scr.normalize_utils import Logging

if __name__ == "__main__":
    logger = Logging.get_logger("web_scraping")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        help="The name of the csv file containing the Source and Event_ID",
        type=str,
    )
    parser.add_argument(
        "-r",
        "--raw_dir",
        dest="raw_dir",
        help="The directory containing raw json files",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
        help="The directory where the output file will land (as .csv)",
        type=str,
    )
    parser.add_argument(
        "-h",
        "--header",
        dest="header",
        help="The header for web scraping",
        type=str,
    )

    args = parser.parse_args()
    logger.info(f"Passed args: {args}")

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    def getHTMLText(url):
        try:
            # change headers to your own IP
            headers = {"User-Agent": args.header}
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r.text

        except:
            return ""

    raw = pd.read_csv(f"{args.raw_dir}/{args.filename}", encoding="ISO-8859-1")

    def process_paragraphs(soup):
        sentences_list = []
        # Find the element with class "p"
        body_content = soup.find_all("p")

        for tag in tqdm.tqdm(body_content):
            sentences_list.append(tag.text)
        return sentences_list

    def process_paragraphs_artemis(soup):
        sentences_list = []
        # Find the element with class "p"
        body_content = soup.find_all(class_="pf-content")

        for tag in tqdm.tqdm(body_content):
            sentences_list.append(tag.text)

        return sentences_list

    # Function to get Wikipedia infobox
    def get_wikipedia_infobox(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")  # the parser is bit different compare to the text

        # Find the infobox using its class name
        infobox = soup.find("table", {"class": "infobox"})

        # You can then extract data from the infobox as needed
        if infobox:
            rows = infobox.find_all("tr")
            infobox_data = {}
            for row in rows:
                header = row.find("th")
                data = row.find("td")
                if header and data:
                    # Use unidecode for both keys and values, then encode and decode with UTF-8
                    key = unidecode(header.text.strip())
                    value = unidecode(data.text.strip())
                    infobox_data[key] = value

            return infobox_data
        else:
            return {}

    event_info = []
    for index, row in raw.iterrows():
        url = str(row["Source"])
        event_id = str(row["Event_ID"])
        html = getHTMLText(url)
        soup = BeautifulSoup(html, "html.parser")
        if "wiki" in url:
            # Extract the title
            title = soup.title.string
            # Remove "- Wikipedia" from the title
            event_name = title.replace(" - Wikipedia", "").strip()
            whole_text = process_paragraphs(soup)
            # Get infobox data and add to 'Info_Box' column
            infobox_data = get_wikipedia_infobox(url)
            info_box_text = "\n".join([f"{key}: {value}" for key, value in infobox_data.items()])
        else:
            whole_text = process_paragraphs_artemis(soup)
            info_box_text = None
            event_name = None  # for artemis article, the event name needs to extract from the article
        event_data = {
            "Source": url,
            "Whole_Text": whole_text,
            "Info_Box": info_box_text,
            "Event_ID": event_id,
            "Event_Name": event_name,
        }

        # Append the event data dictionary to the event list
        event_info.append(event_data)

    event_json = json.dumps(event_info, indent=4)
    logger.info(f"Save result")
    with open(f"{args.raw_dir}/{args.filename.replace('.csv', '.json')}", "w") as file:
        file.write(event_json)
