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
            if item_parsed:  # Check if item_parsed is not None
                articles.append(item_parsed)
        top_articles = articles[:50]
        
        return top_articles

        
    
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

        category = uri.split("/")[3] if len(uri.split("/")) > 3 else ''
        mapped_category = category_map.get(category.lower(), "General")
        
        article_container = {
            "uri": uri,
            "headline": a_tag.text.strip(),
            "category": mapped_category,
            "images": [],
            'ttl': 86400,  # 24 hours
            'ts': current_timestamp
        }

        img_tag = soup.find('img')
        if img_tag:
            src = f"http:{img_tag.get('src')}"
            # Check if the image is not a GIF file
            if not src.lower().endswith('.gif'):
                article_container["images"] = [src]

        # Check if the article has images before returning
        if article_container["images"]:
            hash_object = hashlib.sha256(json.dumps(article_container, sort_keys=True).encode())
            article_container["id"] = hash_object.hexdigest()
            return article_container
    
    return None  # Return None if the article doesn't have images

if __name__ == "__main__":
    
    event = {
        'statusCode': 200, 
        'article_blocks_json_url': 'https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__www.foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJIMOJB6N5&Signature=hEYP2okJhUrIV9VkyxkmTt9I2L8%3D&Expires=1712364087', 
        'article_block_tag': '<article class="article">', 
        'news_site_url': 'https://www.foxnews.com'
    }

    parsed_articles = lambda_handler(event=event, context=None)
    print(parsed_articles)
