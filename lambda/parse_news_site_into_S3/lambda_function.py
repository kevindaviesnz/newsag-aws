# This file: lambda/parse_news_site_into_S3/lambda_function.py
# To install a library in the current directory:
# pip3 install requests --target .
# @todo logging
import requests
import json
import boto3
import re
from bs4 import BeautifulSoup

import logging

# @todo logging
logger = logging.getLogger(__name__)

s3_client = boto3.client('s3')

def lambda_handler(event: list, context: list) -> list:
    
    # @todo add try catch
    news_site_url = event['news_site_url']
                            
    news_site_html = fetch_html_from_news_site(news_site_url)
    
    # Returns an array of articles
    article_blocks = parse_html_into_article_blocks(news_site_html=news_site_html, article_block_tag=event['article_block_tag'])
    
    # Convert containers into json and convert into bytes
    article_blocks_json_data_bytes = json.dumps(article_blocks).encode('utf-8')

    # Generate a unique S3 key for the articles
    s3_key = f'kdaviesnz.{news_site_url.replace("//", "_").replace(":", "_")}.json'

    # Store article bloocks in a bucket as json
    bucket = "kdaviesnz-news-bucket"
    s3_client.put_object(Body=article_blocks_json_data_bytes, Bucket=bucket, Key=s3_key)

    # Generate a presigned URL for the S3 object
    article_blocks_json_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': s3_key},
        ExpiresIn=432000   # URL expiration time (e.g., 5 days)
    )
    
    # Articles JSON url: https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__foxnews.com.json%3FAWSAccessKeyId%3DAKIA42RD47OJM3V6Q2HU%26Signature%3DVjtNNUSaPPVJG0XyxygUIMxnJQU%253D%26Expires%3D1711854291.json?AWSAccessKeyId=AKIA42RD47OJM3V6Q2HU&Signature=t6uNdP5KV1zFHvPWe8q8P8zODyM%3D&Expires=1711854427
    return {
        'statusCode': 200,
        'article_blocks_json_url': article_blocks_json_url,
        'article_block_tag': event['article_block_tag'],
        'news_site_url': event['news_site_url']
    }

        
def fetch_html_from_news_site(news_site_url:str) -> str:
    
    # @todo do we need a try catch here?
    response = requests.get(news_site_url)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.text


def parse_html_into_article_blocks(news_site_html: str, article_block_tag: str, **kwargs) -> list:

    soup = BeautifulSoup(news_site_html, 'html.parser')
    
    # Extract tag name and class attributes from article_block_tag
    match = re.match(r'<([^>\s]+)', article_block_tag)
    if match:
        tag_name = match.group(1)
    else:
        raise ValueError("Invalid article_block_tag format")
    
    class_attr = re.findall(r'class="([^"]*)"', article_block_tag)  # Extract class attribute
    
    # Prepare keyword arguments for find_all function
    find_all_kwargs = {}
    if class_attr:
        find_all_kwargs['class_'] = class_attr
    
    # Extract the news site html article blocks into an array
    article_blocks = [str(element) for element in soup.find_all(name=tag_name, **find_all_kwargs)]
    return article_blocks
    

if __name__ == "__main__":
    
    """
        event = {
        "news_site_url":"https://www.newshub.co.nz/home.html",
        "article_block_tag": "<div class=\"c-NewsTile\"-item>"
    }

    """

    event = {
        "news_site_url":"https://www.foxnews.com",
        "article_block_tag": "<article class=\"article\">"
    }

    result = lambda_handler(event=event, context=None)
    print(result)