# This file: lambda/foxnews/lambda_function.py
# To install a library in the current directory:
# pip3 install requests --target .
# zip -r <output_zip_file> <directory_to_zip>
from bs4 import BeautifulSoup
import json
import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    try:
        raw_articles_data = event['body']
        articles = []
        for item in raw_articles_data:
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
        "statusCode": 200, 
        "article_blocks_json_url": "https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__www.foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJIMOJB6N5&Signature=hEYP2okJhUrIV9VkyxkmTt9I2L8%3D&Expires=1712364087",
        "article_block_tag": "<article class=\"article\">", 
        "news_site_url": "https://www.foxnews.com",
        "body": ["<article class=\"article story-1\">\n<div class=\"m\">\n<a data-adv=\"hp1bt\" data-omtr-intcmp=\"fnhpbt1\" href=\"https://www.foxnews.com/politics/biden-says-he-didnt-do-that-when-asked-about-proclaiming-easter-as-trans-day-of-visibility\">\n<picture>\n<source media=\"(max-width: 767px)\" srcset=\"//a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2024/03/343/193/Biden-Easter-bunny.jpg?tl=1&amp;ve=1, //a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2024/03/686/386/Biden-Easter-bunny.jpg?tl=1&amp;ve=1 2x\"/>\n<source media=\"(min-width: 768px) and (max-width: 1023px)\" srcset=\"//a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2024/03/720/405/Biden-Easter-bunny.jpg?tl=1&amp;ve=1, //a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2024/03/1440/810/Biden-Easter-bunny.jpg?tl=1&amp;ve=1 2x\"/>\n<source media=\"(min-width: 1024px) and (max-width: 1279px)\" srcset=\"//a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2024/03/540/304/Biden-Easter-bunny.jpg?tl=1&amp;ve=1, //a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2024/03/1080/608/Biden-Easter-bunny.jpg?tl=1&amp;ve=1 2x\"/>\n<source media=\"(min-width: 1280px) and (max-width: 1439px)\" srcset=\"//a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2024/03/520/293/Biden-Easter-bunny.jpg?tl=1&amp;ve=1, //a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2024/03/1040/586/Biden-Easter-bunny.jpg?tl=1&amp;ve=1 2x\"/>\n<source media=\"(min-width: 1440px)\" srcset=\"//a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2024/03/627/353/Biden-Easter-bunny.jpg?tl=1&amp;ve=1, //a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2024/03/1254/706/Biden-Easter-bunny.jpg?tl=1&amp;ve=1 2x\"/>\n<img alt=\"President Biden responds to backlash about proclaiming Easter as 'Trans Day of Visibility'\" height=\"405\" src=\"//a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2024/03/720/405/Biden-Easter-bunny.jpg?tl=1&amp;ve=1\" width=\"720\"/>\n</picture>\n<div class=\"kicker default\"><span class=\"kicker-text\">'I DIDN'T DO THAT'</span></div>\n</a>\n</div>\n<div class=\"info\">\n<header class=\"info-header\">\n<h3 class=\"title\">\n<a data-adv=\"hp1bt\" data-omtr-intcmp=\"fnhpbt1\" href=\"https://www.foxnews.com/politics/biden-says-he-didnt-do-that-when-asked-about-proclaiming-easter-as-trans-day-of-visibility\">President Biden responds to backlash about proclaiming Easter as 'Trans Day of Visibility'</a>\n</h3>\n</header>\n<div class=\"content\">\n</div>\n</div>\n</article>"]
    }

    parsed_articles = lambda_handler(event=event, context=None)
    print(parsed_articles)

