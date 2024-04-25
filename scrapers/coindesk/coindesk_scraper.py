# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 16:46:05 2024

@author: UgoGard
"""

import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Setup basic logging configuration
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("cryptonews_scraper.log"),
                        logging.StreamHandler()
                        ])


def fetch_urls(base_url, start_page=1):
    '''
    The purpose of the fetch_urls function is to scrap the article urls
    available on the bitcoin section of the coindesk website and iterate
    through all the pages.

    Parameters
    ----------
    base_url : string
        DESCRIPTION.
    start_page : integer, optional
        DESCRIPTION. The default is 1.

    Returns
    -------
    complete_urls : list
        DESCRIPTION.

    '''

    logging.info("Starting fetch_urls")
    complete_urls = []
    page_exists = True
    page_number = start_page

    # Iterate through all the pages
    while page_exists:
        logging.debug(f"Fetching page: {page_number}")
        page_url = f'{URL}/tag/bitcoin/{page_number}/'
        response = requests.get(page_url)
        if response.status_code != 200:
            break  # Stop if page not found or error occurs

        # Parse the html to retrieve h6 tags containing url
        soup = BeautifulSoup(response.text, 'html.parser')
        h6_tags = soup.find_all('h6', class_='typography__StyledTypography-sc-owin6q-0 bhrWMt')

        if not h6_tags:
            logging.info("Finished fetching urls")
            break  # Stop if no relevant tags found, assuming end of content

        # Extract the url from the h6 tag
        for h6 in h6_tags:
            for a in h6.find_all('a', href=True):
                href = a['href']
                complete_url = href if href.startswith('http') else base_url + href
                complete_urls.append(complete_url)

        print(page_number)
        page_number += 1

    return complete_urls


def extract_article_data(url):
    '''
    The purpose of the extract_article_data function is to extract the title,
    date and text from an article.

    Parameters
    ----------
    url : string
        DESCRIPTION.

    Returns
    -------
    list
        DESCRIPTION.

    '''

    logging.debug(f"Extracting article: {url}")
    # Fetch the webpage content
    response = requests.get(url)
    if response.status_code != 200:
        return ["Error: Page not found or unable to fetch the content"]

    html_content = response.text

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the title
    title_tag = soup.find('h1', class_='typography__StyledTypography-sc-owin6q-0 kbFhjp')
    title = title_tag.get_text(strip=True) if title_tag else "Title not found"

    # Extract the publication date
    date_tag = soup.find('meta', {'property': 'article:published_time'})
    date = date_tag['content'] if date_tag else 'Date not found'

    # Extract the article text, assuming it's contained within <p> tags
    text = ' '.join(p.get_text(strip=True) for p in soup.find_all('p'))

    logging.debug(f"Finished extracting article: {url}")

    return [date, title, url, text]


URL = 'https://www.coindesk.com'

# Fetch all article urls
urls = fetch_urls(URL)
#urls = ['https://www.coindesk.com/business/2024/04/24/jack-dorseys-block-is-building-a-bitcoin-mining-system/','https://www.coindesk.com/podcasts/markets-daily/crypto-update-increasing-adoption-institutional-investors-and-bitcoin/','https://www.coindesk.com/tech/2024/02/17/protocol-latest-tech-news-crypto-blockchain/']

urls = [url for url in urls if "/podcasts/" not in url]

data = []

for url in urls:
    article_data = extract_article_data(url)
    data.append(article_data)

# Create a dataframe to store the news articles data
coindesk_df = pd.DataFrame(data, columns=['date', 'title', 'url', 'text'])

# Convert date to a datetime object and set date as index
# Removing 'UTC' as strptime does not parse timezone names
coindesk_df['date'] = coindesk_df['date'].replace(" UTC", "")
coindesk_df['date'] = pd.to_datetime(coindesk_df['date'], errors='coerce', utc=True)

# Export dataframe to csv
coindesk_df.to_csv('coindesk_data.csv', index=False)
