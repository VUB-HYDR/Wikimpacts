import os
import sys

import requests
from bs4 import BeautifulSoup
import json


from typing import List
from fastapi.encoders import jsonable_encoder
import json 
import pathlib
from pathlib import Path
import pandas as pd 
    
import tqdm
from unidecode import unidecode  # Correct import
from Database.scr.log_utils import Logging
import argparse

# the prompt list need to use the same variable names in our schema, and each key contains 1+ prompts
if __name__ == "__main__":
    import logging
    logger = logging.getLogger("web scraping")

    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        help="The name of the csv file in the <Wikipedia articles> directory",
        type=str,
    )

    parser.add_argument(
        "-r",
        "--raw_dir",
        dest="raw_dir",
        help="The directory containing Wikipedia csv files to be run",
        type=str,
    )

    parser.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
        help="The directory for the output file",
        type=str,
    )

 
   
    args = parser.parse_args()
    logger.info(f"Passed args: {args}")

    logger.info(f"Creating {args.output_dir} if it does not exist!")

    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    df=pd.read_csv(f"{args.raw_dir}/{args.filename}")
# testing the table information extraction from wikipedia 

    def getHTMLText(url):
        try: 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42'}
            r=requests.get(url,headers=headers,timeout=30)
            r.raise_for_status()
            r.encoding=r.apparent_encoding
            return r.text
        
        except :
            return ''
    
    def process_tables(soup):
        # Find all tables
        tables = soup.find_all("table", {"class": "wikitable"})  # Adjust class if needed
        all_tables_data = []
        if tables:
            # Iterate over all tables found
            for table in tables:
                headers = [header.text.strip() for header in table.find_all("th")]
                data = []

                for row in table.find_all("tr")[1:]:  # Skip header row
                    row_data = {}
                    cells = row.find_all(["td", "th"])  # Include both td and th

                    for i in range(min(len(headers), len(cells))):
                        row_data[headers[i]] = cells[i].text.strip()

                    data.append(row_data)

                all_tables_data.append(data)

            return all_tables_data
        else:
            return {}

    

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

    def get_wikipedia_list(url):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "lxml")  # the parser is bit different compare to the text
            list_items = soup.find_all('li')
            if list_items:
                
            # Extract text from each <li> and return as a list
                return [li.get_text(strip=True) for li in list_items]
            else:
                    return []


    def process_paragraphs(soup):
            structured_content = []
            current_section = None

            # Find all relevant elements
            body_content = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5"])

            for tag in tqdm.tqdm(body_content):
                if tag.name in ["h1", "h2", "h3", "h4", "h5"]:
                    if current_section:
                        structured_content.append(current_section)
                    current_section = {"header": tag.text.strip(), "content": []}
                else:  # It's a paragraph
                    if current_section:
                        current_section["content"].append(tag.text.strip())
                    else:
                        # In case there are paragraphs before any header
                        structured_content.append({"header": "Introduction", "content": [tag.text.strip()]})

            # Add the last section if exists
            if current_section:
                structured_content.append(current_section)

            # Combine paragraphs into a single string for each section
            for section in structured_content:
                section["content"] = " ".join(section["content"])

            return structured_content

    event_info = []
    for index, row in df[:10].iterrows():
            url = str(row["Best_Hit"])
            event_id = str(row["Event_ID"])
            html = getHTMLText(url)
            if html: 
                soup = BeautifulSoup(html, "html.parser")
                
                title_tag = soup.title

                if title_tag:
                    title = title_tag.string
                    if title:
                        # Proceed with title manipulation
                        event_name = title.replace(" - Wikipedia", "").strip()
                    else:
                        event_name = None 
                else:
                    
                
                    event_name = None 
                whole_text = process_paragraphs(soup)
                # Get infobox data and add to 'Info_Box' column
                infobox_data = get_wikipedia_infobox(url)
                info_box_text = "\n".join([f"{key}: {value}" for key, value in infobox_data.items()])
                all_tables=process_tables(soup)
                lists=get_wikipedia_list(url)

                event_data = {
                    "Source": url,
                    "Whole_Text": whole_text,
                    "Info_Box": info_box_text,
                    "Event_ID": event_id,
                    "Article_Name": event_name,
                    "All_Tables":all_tables,
                    "Lists":lists
                }

                # Append the event data dictionary to the event list
                event_info.append(event_data)
        

    # Save structure to a JSON file
    logger.info(f"saving web scraping results")
    json_filename = args.filename.replace(".csv", ".json")
    with open(f"{args.output_dir}/{json_filename}", "w", encoding="utf-8") as f:
        json.dump(event_info, f, indent=2, ensure_ascii=False)
