from bs4 import BeautifulSoup
import json
import requests
import boto3
import uuid

s3_client = boto3.client('s3')

def foxnews_parse_article_content(article_element: str):
    soup = BeautifulSoup(article_element, 'html.parser')
    
    # Find the heading tag and a tag within it
    heading_tag = soup.find('header')
    a_tag = heading_tag.find('a', {'data-omtr-intcmp': True}) if heading_tag else None
    
    if a_tag:
        uri = a_tag.get('href')
        uuid_base = a_tag.get("data-omtr-intcmp")
        uri_suffix = uri.rsplit("/", 1)[-1].replace("-", "_")

        article_container = {
            "uri": uri,
            "headline": a_tag.text.strip(),
            "uuid": f"{uuid_base}{uri_suffix}",
            "categories": [uri.split("/")[3] if len(uri.split("/")) > 3 else None],
            "images": [],
            'ttl': "86400",  # 24 hours
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
    response = requests.get(event["presigned_url"])
    response.raise_for_status()  # Raise an exception for HTTP error responses
    articles_json = response.json()  # This method parses the JSON response into a Python dict or list
    event["Items"] = articles_json
    articles = []
    for item in event['Items']:
        item_parsed = foxnews_parse_article_content(item)
        if (item_parsed != None):
            articles.append(item_parsed)
    top_articles = articles[:10]
    return top_articles


if __name__ == "__main__":
    event = {
        "presigned_url":"https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJM3V6Q2HU&Signature=bm9CN7GsuUmb0M6VrQWdjiVysCI%3D&Expires=1711163704",
        "tag": "article"        
    }
    parsed_articles = lambda_handler(event=event, context=None)
    print(parsed_articles)
