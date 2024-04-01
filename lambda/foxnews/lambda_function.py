# This file: lambda/foxnews/lambda_function.py
from bs4 import BeautifulSoup
import json
import requests
import boto3
import uuid
import datetime

import logging

logger = logging.getLogger(__name__)

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # json items are contained in the `Items` array
    try:
        response = requests.get(event["article_blocks_json_url"])
        response.raise_for_status()  # Raise an exception for HTTP error responses
        articles_json = response.json()  # This method parses the JSON response into a Python dict or list
        event["Items"] = articles_json
        articles = []
        for item in event['Items']:
            item_parsed = foxnews_parse_article_content(item)
            if (item_parsed != None):
                articles.append(item_parsed)
        top_articles = articles[:50]
        return top_articles
    
    except Exception as err:

        logger.error(
            "Error when parsing news data into json. %s: %s", 
            err.response["Error"]["Code"], 
            err.response["Error"]["Message"]
        )

        return {
            'statusCode':500,
            'error': err
        }


def foxnews_parse_article_content(article_element: str):
    soup = BeautifulSoup(article_element, 'html.parser')
    
    # Find the heading tag and a tag within it
    heading_tag = soup.find('header')
    a_tag = heading_tag.find('a', {'data-omtr-intcmp': True}) if heading_tag else None
    
    if a_tag:
        uri = a_tag.get('href')

        # Get current timestamp in seconds
        current_timestamp = int(datetime.datetime.now().timestamp())

        article_container = {
            "uri": uri,
            "headline": a_tag.text.strip(),
            "uuid": str(uuid.uuid4()),
            "category": uri.split("/")[3] if len(uri.split("/")) > 3 else '',
            "images": [],
            'ttl': 86400,  # 24 hours
            'ts': current_timestamp
        }

        # Find picture and img tags
        img_tag = soup.find('img')
        if img_tag:
            src = f"http:{img_tag.get('src')}"
            article_container["images"] = [src] 

        return article_container
    
    else:

        return None

if __name__ == "__main__":
    event = {
        "statusCode": 200, 
        "article_blocks_json_url": "https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__www.foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJIMOJB6N5&Signature=hEYP2okJhUrIV9VkyxkmTt9I2L8%3D&Expires=1712364087",
        "article_block_tag": "<article class=\"article\">", 
        "news_site_url": "https://www.foxnews.com"
    }
    parsed_articles = lambda_handler(event=event, context=None)
    print(parsed_articles)
