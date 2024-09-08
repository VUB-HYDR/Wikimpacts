*** This is the web scraping process ***

[] Wikipedia_articles/Web_scraping_wiki.py is the script for web scraping, and process the whole text as a header-content pair, which is the web scraping process of EN Wiki articles used for prompt V_3
[] Wikipedia_articles/Web_scraping_wiki_artemis_NLP2024.py is the script for web scraping applied in the paper https://github.com/VUB-HYDR/Wikimpacts/releases/tag/v0.1
[] Wikipedia_articles/wiki_whole_infobox_20240730_5046_events.json is the result from this script
[] classified_articles_Wikipedia_whole_infobox_5046record.csv is the result from the version of script using in the NLP paper, which contains the whole text without header-content pair



***Tips***
Google Chrome / Firefox / Edge:
    Open your browser.
    Right-click anywhere on the page and press Ctrl + Shift + I to open Developer Tools).
    Go to the Network tab.
    Reload the page, and you'll see network requests being logged.
    Click on one of the network requests (such as the page request).
    Under the Headers tab, scroll down to the Request Headers section, where you'll find User-Agent.

***Notes***
This part is not including in the https://github.com/VUB-HYDR/Wikimpacts/releases/tag/v0.1
