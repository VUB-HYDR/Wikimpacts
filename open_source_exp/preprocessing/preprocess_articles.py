import os
import pickle
import re
import shutil
from urllib.parse import unquote
import json
import pandas as pd
import requests
import wikipediaapi
from bs4 import BeautifulSoup
from unidecode import unidecode
from urls import url_list
excluded_sections = [
    "See also",
    "References",
    "Sources",
    "Further reading",
    "External links"
]


def preprocess_text(text):
    # Remove special characters and unnecessary spaces
    text = text.replace("\n\n", "\n")
    # Normalize text: lowercase and punctuation spacing
    text = text.replace(" ,", ",").replace(" .", ".").replace(" (", "(").replace(" )", ")").replace(" ;", ";").replace(" :", ":").replace('“', '"').replace('”', '"')
    text = text.split("Also read:")[0]
    text = text.split("Other recent articles ")[0]
    text = text.strip()
    return text

# Function to get Wikipedia infobox
def get_wikipedia_infobox(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    # Find the infobox using its class name
    infobox = soup.find('table', {'class': 'infobox'})

    # You can then extract data from the infobox as needed
    if infobox:
        rows = infobox.find_all('tr')
        infobox_data = {}
        for row in rows:
            header = row.find('th')
            data = row.find('td')
            if header and data:
                # Use unidecode for both keys and values, then encode and decode with UTF-8
                key = unidecode(header.text.strip())
                value = unidecode(data.text.strip())
                infobox_data[key] = value

        #info_box = '\n'.join([f"{key}: {value}" for key, value in infobox_data.items()])
        info_box = str(infobox_data)
        return info_box
    else:
        return {}


def process_wikipedia_article(link):
    title = link.split("/")[-1]
    info_box = get_wikipedia_infobox(link)
    try:
        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent='MyProjectName (merlin@example.com)',
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )
        # Fetch the page
        page = wiki_wiki.page(title)
        # Check if the page exists
        if not page.exists():
            print(f"The page {title} does not exist.")
            return None
        article_content = page.summary + "\n"

        # Recursive function to fetch content from all sections and subsections, excluding specified ones
        def get_content(sections, level=0):
            nonlocal article_content
            for section in sections:
                if section.title not in excluded_sections:
                    # Add section title and content
                    title_sep = "-"*(level+1)
                    article_content += f"{title_sep}{section.title}{title_sep}\n{section.text}\n"
                    get_content(section.sections, level + 1)

        # Get content from all sections and subsections
        get_content(page.sections)
        return preprocess_text(article_content), info_box
    except Exception as e:
        print(e, link)
        return None, None


def process_artemis_articles(link):
    link_list = list(set(link.split("|")))
    articles = [""]
    for url in link_list:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        article = soup.find('div', class_='pf-content')  # Use the specific class to find the content

        if article:

            title_div = soup.find('div', class_='p-3 bg-news white')
            title = title_div.find('h1').get_text() if title_div else "Title not found"

            paragraphs = article.find_all('p')
            text = []
            for para in paragraphs:

                if para.find_parent('div', class_='artem-bottom-ad') or (para.has_attr('style')):
                    continue
                text.append(para.get_text())
            text = f"---{title}---\n" + preprocess_text("\n".join(text))
            articles.append(text)

    return '\n'.join(articles)


def download_articles(article_links, save_dir, url_to_event_name, url_to_event_id):
    for i, link in enumerate(article_links):
        print(link)
        try:
            page_name = url_to_event_name[link]
            event_id = url_to_event_id[link]

            page_name_escaped = page_name.replace('/', '_')
        except:
            print("NO EVENT NAME IN THE EXCEL")
            exit()
        link_str = unquote(link)

        if "wiki" in link:
            try:
                article_content, info_box = process_wikipedia_article(link_str)
            except:
                print("Error:", link)
                continue
        else:
            article_content = process_artemis_articles(link_str)
            info_box = None

        filename = os.path.join(save_dir, f"{page_name_escaped}.pickle")
        with open(filename, 'wb') as f:
            pickle.dump({"text": article_content, "info_box": info_box, "event_name": page_name, "URL": link, "Event_ID": event_id}, f)


if __name__ == "__main__":

    problematic_urls = {
        "https://en.wikipedia.org/wiki?curid=7870060": "https://en.wikipedia.org/wiki/Drought_in_Australia",
        "https://en.wikipedia.org/wiki?curid=51630189": "https://en.wikipedia.org/wiki/2006-2008_Southeastern_United_States_drought",
        "https://en.wikipedia.org/wiki?curid=5589427": "https://en.wikipedia.org/wiki/Cyclone_Steve",
        "https://en.wikipedia.org/wiki?curid=61000334": "https://en.wikipedia.org/wiki/Cyclone_Vayu",
    }

    df_dev = pd.read_excel("excels/100events_validation_text_infobox_240507_multi (1).xlsx", sheet_name="Sheet1")
    df_gold = pd.read_excel("excels/test_182_single_event_infobox_wholetext.xlsx", sheet_name="Sheet1")
    df_dev['URL'] = df_dev['URL'].replace(problematic_urls)
    df_gold['URL'] = df_gold['URL'].replace(problematic_urls)

    df_combined = pd.concat([df_dev[['URL', 'Event_Name', 'Event_ID']], df_gold[['URL', 'Event_Name', 'Event_ID']]])

    # Drop duplicates if any
    df_combined = df_combined.drop_duplicates()

    # Create the dictionary
    url_to_event_name = pd.Series(df_combined.Event_Name.values, index=df_combined.URL).to_dict()
    url_to_event_name = {url.strip(): event_name.strip() for url, event_name in zip(df_combined.URL, df_combined.Event_Name)}

    url_to_event_id = pd.Series(df_combined.Event_ID.values, index=df_combined.URL).to_dict()
    url_to_event_id = {url.strip(): event_name.strip() for url, event_name in zip(df_combined.URL, df_combined.Event_ID)}

    for k, v in url_list.items():
        save_dir = f"preprocessed_articles/{k}"
        try:
            shutil.rmtree(save_dir)
        except: pass
        os.makedirs(save_dir, exist_ok=True)
        download_articles(v, save_dir, url_to_event_name, url_to_event_id)