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
    """
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
    
    def process_tables(soup):
        tables = soup.find_all("table", {"class": "wikitable"})
        all_tables_data = []

        if tables:
            for table in tables:
                headers = [header.text.strip() for header in table.find_all("th")]
                data = []
                last_row_data = None # To keep track of the previous valid dict

                for row in table.find_all("tr")[1:]:
                    cells = row.find_all(["td", "th"])

                    # If only 1 cell and fewer than headers: likely a description row to merge
                    if len(cells) == 1 and len(headers) > 1:
                        # Attach as new field to previous dict if it exists
                        if last_row_data is not None:
                            # Choose your field name below, e.g. "Description" or "Summary"
                            last_row_data["Description"] = cells[0].text.strip()
                    else:
                        # Normal row; build dict per headers
                        row_data = {}
                        for i in range(min(len(headers), len(cells))):
                            row_data[headers[i]] = cells[i].text.strip()
                        data.append(row_data)
                        last_row_data = row_data # Update pointer

                all_tables_data.append(data)
            return all_tables_data
        else:
            return []
    
    def process_tables(soup):
        tables = soup.find_all("table", class_="wikitable")
        all_tables_data = []
        if not tables:
            return []

        for table in tables:
            # Get headers from the first row
            headers = [hd.get_text(strip=True) for hd in table.find("tr").find_all(["td", "th"])]
            data = []
            group_col = headers[0]  # Use first column header as grouping key
            detail_headers = headers[1:]
            current_group = None

            for row in table.find_all("tr")[1:]:
                cells = row.find_all(["td", "th"])
                # Handle rows with only 1 cell (e.g. description rows)
                if len(cells) == 1 and len(headers) > 1:
                    # Attach description or details as a new field to current group
                    if current_group is not None:
                        # You may use 'Description' or 'Details' as the field name
                        # Append as a list if you want to accommodate multiple description rows
                        desc = cells[0].get_text(strip=True)
                        current_group.setdefault("Description", []).append(desc)
                    continue

                # Rowspan: if the first cell present, new group; else, extend the last group
                group_val = cells[0].get_text(strip=True) if cells else ""
                is_new_group = group_val != "" and (current_group is None or group_val != current_group[group_col])

                if is_new_group:
                    current_group = {group_col: group_val, "events": []}
                    data.append(current_group)

                # Build the details dict (may be fewer cells than detail_headers)
                # If first cell is present, details start from cell 1, else from cell 0
                cell_offset = 1 if group_val != "" else 0
                details = {}
                for i, header in enumerate(detail_headers):
                    idx = i + cell_offset
                    details[header] = cells[idx].get_text(strip=True) if idx < len(cells) else ""
                # Only append non-empty details (unless you want summary rows, etc.)
                if any(details.values()):
                    current_group["events"].append(details)

            all_tables_data.append(data)
        return all_tables_data
    
    def process_tables(soup):
        tables = soup.find_all("table", class_="wikitable")
        all_tables_data = []
        if not tables:
            return []

        for table in tables:
            # 1. Try to find a header row (tr containing th)
            header_row = None
            for tr in table.find_all("tr"):
                if tr.find("th"):
                    header_row = tr
                    break

            if header_row is not None:
                headers = [th.get_text(strip=True) for th in header_row.find_all(["td", "th"])]
                group_col = headers[0]
                detail_headers = headers[1:]

                # Identify all rows after header_row
                tr_list = list(table.find_all("tr"))
                header_idx = tr_list.index(header_row)
                data_rows = []
                for tr in tr_list[header_idx+1:]:
                    tds = tr.find_all("td")
                    if tds:
                        data_rows.append(tds)

                data = []
                current_group = None
                for tds in data_rows:
                    first_cell = tds[0].get_text(strip=True) if tds else ""
                    is_new_group = first_cell != "" and (current_group is None or first_cell != current_group[group_col])
                    if is_new_group:
                        current_group = {group_col: first_cell, "events": []}
                        data.append(current_group)

                    detail_cells = [td.get_text(strip=True) for td in tds[1:]]
                    details = dict(zip(detail_headers, detail_cells))
                    if any(details.values()):
                        current_group["events"].append(details)
                all_tables_data.append(data)

            else:
                # No header row: treat as a plain table, output as a list of lists of text
                # Optionally, could also just skip, or try to infer columns if you want
                plain_rows = []
                for tr in table.find_all("tr"):
                    tds = tr.find_all("td")
                    if tds:
                        plain_rows.append([td.get_text(strip=True) for td in tds])
                all_tables_data.append(plain_rows)
        return all_tables_data
    """
    def process_tables(soup):
        # Find all tables (class can be adjusted if necessary)
        tables = soup.find_all("table", {"class": "wikitable"})
        all_tables_data = []
        if not tables:
            return all_tables_data
        # Iterate over each table
        for table in tables:
            table_rows = []
            # Find all the rows in this table
            rows = table.find_all("tr")

            for row in rows:
                # Gather all cells in the row (both <td> and <th>)
                cells = row.find_all(["td", "th"])
                # Convert each cell to stripped text
                row_data = [cell.get_text(strip=True) for cell in cells]
                table_rows.append(row_data)

            all_tables_data.append(table_rows)

        return all_tables_data
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
    for index, row in df.iterrows():
            url = str(row["Source"])
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
                if isinstance(event_name, str) and "list" in event_name.lower():
                    lists = get_wikipedia_list(url)
                else:
                    lists = []

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
