# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 15:11:59 2024

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


def fetch_urls():
    '''
    The purpose of the extract_article_data function is to extract the title,
    date and text from an article.

    Returns
    -------
    complete_urls : string
        DESCRIPTION.

    '''
    
    logging.info("Starting fetch_urls")
    base_url = "https://cryptonews.com/news/bitcoin-news"
    complete_urls = []
    page = 1

    while True:
        logging.debug(f"Fetching page: {page}")
        if page == 1:
            url = base_url + "/"
        else:
            url = f"{base_url}/page/{page}/"
        
        # Fetch the content from the URL
        response = requests.get(url)
        webpage_content = response.text

        # Parse the HTML content
        soup = BeautifulSoup(webpage_content, 'html.parser')

        # Find all <div> elements with the class 'news-one-title'
        news_titles = soup.find_all('div', class_='news-one-title')

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
    
    print("URLs extraction completed")
    
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
    response = requests.get(url)
    webpage_content = response.text
    soup = BeautifulSoup(webpage_content, 'html.parser')

    # Extract the title
    title_tag = soup.find('h1', class_='mb-10')
    title = title_tag.text.strip() if title_tag else 'Title not found'

    # Extract the date    
    date_tag = soup.find('meta', {'property': 'article:published_time'})
    date = date_tag['content'] if date_tag else 'Date not found'

    # Extracting the article text
    article_content_tag = soup.find('div', class_='article-single__content category_contents_details')
    text = ' '.join([p.text for p in article_content_tag.find_all('p')]) if article_content_tag else 'Content not found'

    logging.debug(f"Finished extracting article: {url}")

    return [date, title, url, text]


# Fetch urls from all available pages
urls = fetch_urls()
#urls = ['https://cryptonews.com/news/bitcoin-and-ethereum-on-their-way-to-mass-market-1649.htm']

data = []

for url in urls:
    article_data = extract_article_data(url)
    data.append(article_data)

# Create a dataframe to store the news articles data
cryptonews_df = pd.DataFrame(data, columns=['date', 'title', 'url', 'text'])

# Convert date to a datetime object and set date as index
# Removing 'UTC' as strptime does not parse timezone names
#cryptonews_df['date'] = cryptonews_df['date'].replace(" UTC", "")
cryptonews_df['date'] = pd.to_datetime(cryptonews_df['date'], errors='coerce', utc=True)
#cryptonews_df = cryptonews_df.set_index(cryptonews_df['date'])

# Export dataframe to csv
cryptonews_df.to_csv('cryptonews_data.csv')
