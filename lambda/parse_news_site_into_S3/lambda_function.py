# This file: lambda/fetch_html/lambda_function.py
# To install a library in the current directory:
# pip3 install requests --target .
# @todo logging
import requests
import json
import boto3
import re
from bs4 import BeautifulSoup

import logging

logger = logging.getLogger(__name__)


s3_client = boto3.client('s3')

def lambda_handler(event: list, context: list) -> list:
    
    try: 

        news_site_url = event['news_site_url']
                              
        news_site_html = fetch_html_from_news_site(news_site_url, event['container_tag'])
        containers = parse_html_into_containers(news_site_html, event['container_tag'])
        
        # Convert containers into json and convert into bytes
        containers_json_data_bytes = json.dumps(containers).encode('utf-8')
        
        # Generate a unique S3 key for the articles
        s3_key = f'kdaviesnz.{news_site_url.replace("//", "_").replace(":", "_")}.json'

        # Store articles in a bucket
        bucket = "kdaviesnz-news-bucket"
        s3_client.put_object(Body=containers_json_data_bytes, Bucket=bucket, Key=s3_key)

        # Generate a presigned URL for the S3 object
        containers_json_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': s3_key},
            ExpiresIn=432000   # URL expiration time (e.g., 5 days)
        )

    except Exception as err:

        logger.error(
            "Error when parsing news site. %s: %s", 
            err.response["Error"]["Code"], 
            err.response["Error"]["Message"]
        )

        return {
            'statusCode':500,
            'error': err
        }
    
    # Articles JSON url: https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__foxnews.com.json%3FAWSAccessKeyId%3DAKIA42RD47OJM3V6Q2HU%26Signature%3DVjtNNUSaPPVJG0XyxygUIMxnJQU%253D%26Expires%3D1711854291.json?AWSAccessKeyId=AKIA42RD47OJM3V6Q2HU&Signature=t6uNdP5KV1zFHvPWe8q8P8zODyM%3D&Expires=1711854427
    return {
        'statusCode': 200,
        'containers_json_url': containers_json_url,
        'container_tag': event['container_tag'],
        'news_site_url': event['news_site_url']
    }
    
def extract_tag_chunks(text:str, tag: str) -> list:
    pattern = r"<" + tag + r".*?</" + tag + r">"
    chunks = re.findall(pattern, text, re.DOTALL)
    return chunks

def fetch_html_from_news_site(news_site_url:str, container_tag: str) -> str:
    
    response = requests.get(news_site_url)
    response.raise_for_status()  # Raise an exception for bad status codes
    html_content = response.text

    containers_html = extract_tag_chunks(html_content, container_tag)
    
    # Convert elements_data to JSON string
    return json.dumps(containers_html)

def parse_html_into_containers(news_site_html: str, container_tag: str) ->list:

    soup = BeautifulSoup(news_site_html, 'html.parser')
    container_tag = container_tag

    # Extract the containers html directly into an array
    return [element.prettify() for element in soup.find_all(container_tag)]




if __name__ == "__main__":
    
    event = {
        "news_site_url":"https://foxnews.com",
        "container_tag":"article"
    }
    
    result = lambda_handler(event=event, context=None)
    print(result)