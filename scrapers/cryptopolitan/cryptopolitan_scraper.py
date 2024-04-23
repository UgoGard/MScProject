# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 09:11:09 2024

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

    Returns
    -------
    complete_urls : string
        DESCRIPTION.

    '''
    
    logging.info("Starting fetch_urls")
    base_url = "https://www.cryptopolitan.com/news/bitcoin-btc"
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

        # Find all <div> elements with the class 'elementor-heading-title elementor-size-default'
        news_titles = soup.find_all('h3', class_='elementor-heading-title elementor-size-default')

        # Check if the page has news titles
        if len(news_titles) == 1:
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
    try:
        title_tag = soup.find('h1', class_='elementor-heading-title elementor-size-default')
        title = title_tag.text.strip() if title_tag else 'Title not found'
    except:
        title = 'Title not found'

    # Extract the date
    try:
        date_tag = soup.find('span', class_='elementor-icon-list-text elementor-post-info__item elementor-post-info__item--type-date')
        date = date_tag.text.strip() if date_tag else 'Date not found'
    except:
        date = 'Date not found'

    # Extracting the article text
    try:
        page_content_tag = soup.find('div', class_='elementor-element elementor-element-e3418d0 cp-post-content elementor-widget elementor-widget-theme-post-content')
        article_content_tag = page_content_tag.find('div', class_='elementor-widget-container')

        text = ' '.join([p.text for p in article_content_tag.find_all('p')]) if article_content_tag else 'Content not found'
    except:
        text = 'Text not found'

    logging.debug(f"Finished extracting article: {url}")

    return [date, title, url, text]


# Fetch urls from all available pages
urls = fetch_urls(headers)
#urls = ['https://www.cryptopolitan.com/bitcoin-ordinals-garner-attention-nft-space/', 'https://www.cryptopolitan.com/bitcoin-surges-to-a-new-all-time-high/', 'https://www.cryptopolitan.com/price-prediction/']

data = []

for url in urls:
    try:
        article_data = extract_article_data(url, headers)
        data.append(article_data)
    except:
        pass

# Create a dataframe to store the news articles data
cryptopolitan_df = pd.DataFrame(data, columns=['date', 'title', 'url', 'text'])

# Convert date to a datetime object and set date as index
cryptopolitan_df['date'] = pd.to_datetime(cryptopolitan_df['date'], errors='coerce', utc=True)

# Export dataframe to csv
cryptopolitan_df.to_csv('cryptopolitan_data.csv', index=False)
