# This file: lambda/newshub/lambda_function.py
# To install a library in the current directory:
# pip3 install requests --target .
from bs4 import BeautifulSoup
import json
import requests
import uuid
import datetime
import hashlib

import logging

# @todo logging
logger = logging.getLogger(__name__)


def lambda_handler(event, context):

    try:
        response = requests.get(event["article_blocks_json_url"])
        response.raise_for_status()  # Raise an exception for HTTP error responses
        articles_json = response.json()  # This method parses the JSON response into a Python dict or list
        event["Items"] = articles_json
        articles = []
        for item in event['Items']:
            item_parsed = newshub_parse_article_content(item)
            if (item_parsed != None):
                articles.append(item_parsed)
        top_articles = articles[:50]
        return top_articles
    
    except Exception as err:

        logger.error(
            "Error when parsing news data into json. %s: %s", 
        )

        return {
            'statusCode':500,
            'error': err
        }


def newshub_parse_article_content(article_element: str):

    soup = BeautifulSoup(article_element, 'html.parser')
    
    # Find the heading tag and a tag within it
    a_tag = soup.find('a')

    
    if a_tag:

        uri = a_tag.get('href')
        headline = soup.find('h3').text.strip()

        category_map = {
            "sports":"Sports",
            "world": "World",
            "lifestyle": "Lifestyle",
            "politics":"Politics",
            "media": "Media",
            "category": "General",
            "entertainment": "Entertainment",
            "video":"General",
            "us": "World",
            "fox-news-travel": "Lifestyle",
            "money": "Business",
            "health": "Lifestyle",
            "markets": "Business",
        }

        category_container = soup.find('div', class_='c-NewsTile-storyTag')
        category = category_container.find('a').text.strip()

        mapped_category = category_map.get(category.lower(), "General")

        # Get current timestamp in seconds
        current_timestamp = int(datetime.datetime.now().timestamp())

        article_container = {
            "uri": uri,
            "headline": headline,
            "uuid": str(uuid.uuid4()),
            "category": mapped_category,
            "images": [],
            'ttl': 86400,  # 24 hours
            'ts': current_timestamp
        }

        # Find picture and img tags
        img_tag = soup.find('img')
        if img_tag:
            src = img_tag.get('srcset')
            article_container["images"] = [src] 

        hash_object = hashlib.sha256(json.dumps(article_container, sort_keys=True).encode())
        article_container["id"] = hash_object.hexdigest()

        return article_container
    
    else:

        return None


if __name__ == "__main__":
    event = {
        "statusCode": 200,
        'article_blocks_json_url': 'https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__www.newshub.co.nz/home.html.json?AWSAccessKeyId=AKIA42RD47OJIMOJB6N5&Signature=fT6%2BSyqZfXFtwa5N5UWOh1PgL8Q%3D&Expires=1712459212',
        "article_block_tag": "<div class=\"c-NewsTile\"-item>",
        "news_site_url": "https://www.newshub.co.nz/home.html"        
    }
    parsed_articles = lambda_handler(event=event, context=None)
    print(parsed_articles)
