# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 08:31:28 2024

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

# Define headers to mimic a browser request
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


def fetch_urls(headers):
    '''
    The purpose of the extract_article_data function is to extract the title,
    date and text from an article.

    Parameters
    ----------
    headers : dict
        DESCRIPTION.

    Returns
    -------
    list
        DESCRIPTION.

    '''
    
    logging.info("Starting fetch_urls")    
    base_url = 'https://beincrypto.com/bitcoin-news'
    complete_urls = []
    page = 1

    while True:
        logging.debug(f"Fetching page: {page}")
        if page == 1:
            url = base_url + "/"
        else:
            url = f"{base_url}/page/{page}/"
        
        # Fetch the content from the URL
        response = requests.get(url, headers=headers)
        webpage_content = response.text

        # Parse the HTML content
        soup = BeautifulSoup(webpage_content, 'html.parser')

        # Find all <div> elements with the class 'news-one-title'
        news_titles = soup.find_all('h5', class_="h-full s2 s2--medium mb-2 lg:s1 lg:s1--medium")

        # Check if the page has news titles
        if not news_titles:
            logging.info("Finished fetching urls")
            break  # Break the loop if no news titles found, indicating the end of the pages

        # Extract the href and text for each <a> tag within each found <div>
        for title in news_titles:
            a_tag = title.find('a')
            if a_tag:
                href = a_tag.get('href')  # Get the href attribute
                complete_urls.append(href)
        
        page += 1  # Go to the next page
    
    return complete_urls


def extract_article_data(url, headers):
    '''
    The purpose of the extract_article_data function is to extract the title,
    date and text from an article.

    Parameters
    ----------
    url : string
        DESCRIPTION.
    
    headers : dict
        DESCRIPTION.

    Returns
    -------
    list
        DESCRIPTION.

    '''
    
    logging.debug(f"Extracting article: {url}")
    response = requests.get(url, headers=headers)
    webpage_content = response.text
    soup = BeautifulSoup(webpage_content, 'html.parser')

    # Extract the title
    title_tag = soup.find('h1', class_='h4 lg:h1 mt-3 mb-2 lg:mb-3 w-full')
    title = title_tag.text.strip() if title_tag else 'Title not found'

    # Extract the date
    date_tag = soup.find('div', class_='flex flex-col gap-y-1')
    date = date_tag.time.get('datetime') if date_tag else 'Date not found'

    # Extracting the article text
    article_content_tag = soup.find('div', class_='entry-content-inner')
    text = ' '.join([p.text for p in article_content_tag.find_all('p')]) if article_content_tag else 'Content not found'

    logging.debug(f"Finished extracting article: {url}")

    return [date, title, url, text]


# Fetch urls from all available pages
urls = fetch_urls(headers)
#urls = ['https://beincrypto.com/bitcoin-expert-predicts-price-boom/', 'https://beincrypto.com/days-before-bitcoin-halving/', 'https://beincrypto.com/mathematician-future-economics-quantum-bitcoin/']

data = []

for url in urls:
    try:
        article_data = extract_article_data(url, headers)
        data.append(article_data)
    except:
        pass

# Create a dataframe to store the news articles data
beincrypto_df = pd.DataFrame(data, columns=['date', 'title', 'url', 'text'])

# Convert date to a datetime object and set date as index
beincrypto_df['date'] = pd.to_datetime(beincrypto_df['date'], errors='coerce', utc=True)

# Export dataframe to csv
beincrypto_df.to_csv('beincrypto_data.csv', index=False)
