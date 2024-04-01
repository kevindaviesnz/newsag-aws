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

def lambda_handler(event, context):
    # json items are contained in the `Items` array
    try:
        response = requests.get(event["containers_json_url"])
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


if __name__ == "__main__":
    event = {
        "statusCode": 200,
        "article_blocks_json_url": "https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__www.newshub.co.nz/home.html.json?AWSAccessKeyId=ASIA42RD47OJCQS5ZU4A&Signature=2pq23alzH9BCGndCjb4FF0RTYeE%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEA8aDmFwLXNvdXRoZWFzdC0yIkcwRQIhAL%2BanpGXq6XkFZIx7IN%2BKyuQ%2BgvKesmVz0xSTZVLZABOAiAOHQlOLQW5EsaiaEeFuEHU%2BdFcypFbj5rIdGOjETC4rSqIAwg4EAAaDDg4MTYxNzMzNzIzNCIMyJawiWDboerffOi%2FKuUChaCLy1TWT%2FfZw%2BYvK3Vemhf%2FVib0PuaIhwO4rgJgoSXB2gInzMwDgWFhGQI0XSJtfEcmE1uw4HG5QJeijRb5jA94mLRjA7xnayEU6E1pIep9%2FjBEmYJ%2FHPNFyx07JoTjl8aqBsr8vc0c2wFfAYZWLdAkREFGXmwgABeMqQ%2BRturh%2BX%2BIuqUiKMelSwfBRFSskyUBfmVUKMH1hDsvjdtyT4ee8nPFkDJXS3%2FjjAgUp6VfaqDYHPksjojIYqyjuzyHHD9%2B96RrZBJ9b1K74RqquErTuMzIJUURzLfcNENCIbMg996WsifGgr%2FwHkJtJIfVUT1HYIJQCSmbKs9901L8VgN5Yjj7vSBRA82%2FmzXBWZJKl1LpWNZSnvjfQrxISRB4ZVhNL8XuGRIl25A73zOy9XkbSeJYYoM8VKzJriFAAEPGokf5HdGixWa114B2dCCe%2FmPogee1s3JsHtO13wrVdR4J3cedMPPIp7AGOp0BSilS8MKcQHab4SeCWQI6gOlfnqkYvJq0MuZq4w9CKAj314Dus96%2FrUVCcMtgmGx0K5aE%2FmhugMx24rENkCi1wXc5DNJLHrYEnIKPJOSkJmXoc9sa8W9sbG6VSMcib5D5v2DKptKM7ATAnnHORtG9X9BZrDidxOI4pnz%2BAUfGIT8m60ug%2Fy%2FhQVGCFFGbQ7MGjtvevVkWPA8yezQ0uw%3D%3D&Expires=1712356616",
        "article_block_tag": "<div class=\"c-NewsTile\"-item>",
        "news_site_url": "https://www.newshub.co.nz/home.html"
    }
    parsed_articles = lambda_handler(event=event, context=None)
    print(parsed_articles)
