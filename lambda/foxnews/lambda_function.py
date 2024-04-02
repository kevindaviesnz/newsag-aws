# This file: lambda/foxnews/lambda_function.py
# To install a library in the current directory:
# pip3 install requests --target .
# zip -r <output_zip_file> <directory_to_zip>
from bs4 import BeautifulSoup
import requests
import json
import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
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
        
        return {
            "statusCode": 200,
            "body": json.dumps(top_articles),
            "article_block_tag": event["article_block_tag"],
            "news_site_url": event["news_site_url"]
        }
    
    except Exception as err:
        logger.error("Error when parsing news data into json. %s", err)
        return {
            'statusCode':500,
            'error': str(err)
        }

def foxnews_parse_article_content(article_element: str):
    soup = BeautifulSoup(article_element, 'html.parser')
    
    heading_tag = soup.find('header')
    a_tag = heading_tag.find('a', {'data-omtr-intcmp': True}) if heading_tag else None
    
    if a_tag:
        uri = a_tag.get('href')
        current_timestamp = int(datetime.datetime.now().timestamp())

        article_container = {
            "uri": uri,
            "headline": a_tag.text.strip(),
            "category": uri.split("/")[3] if len(uri.split("/")) > 3 else '',
            "images": [],
            'ttl': 86400,  # 24 hours
            'ts': current_timestamp
        }

        img_tag = soup.find('img')
        if img_tag:
            src = f"http:{img_tag.get('src')}"
            article_container["images"] = [src] 

        hash_object = hashlib.sha256(json.dumps(article_container, sort_keys=True).encode())
        article_container["id"] = hash_object.hexdigest()
        
        return article_container
    
    else:
        return None

if __name__ == "__main__":
    
    event = {
        'statusCode': 200, 
        'article_blocks_json_url': 'https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__www.foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJIMOJB6N5&Signature=hEYP2okJhUrIV9VkyxkmTt9I2L8%3D&Expires=1712364087', 
        'article_block_tag': '<article class="article">', 
        'news_site_url': 'https://www.foxnews.com'
    }


    parsed_articles = lambda_handler(event=event, context=None)
    print(parsed_articles)

