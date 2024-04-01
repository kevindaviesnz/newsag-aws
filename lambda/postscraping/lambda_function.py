import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError, ValidationError

logger = logging.getLogger(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('NewsArticles') 

def lambda_handler(event, context):
    
    try:
        articles = event['body'] 
        filtered_articles = list(filter(filter_existing_articles, articles))
        return filtered_articles
  
    except ValidationError as err:
        
        logger.error(
            "Validation error. %s: %s", 
            err.response["Error"]["Code"], 
            err.response["Error"]["Message"]
        )

        raise

    except ClientError as err:
        
        logger.error(
            "Client error!!!. %s: %s", 
            err.response["Error"]["Code"], 
            err.response["Error"]["Message"]
        )

        raise
          

def filter_existing_articles(article):
    response = table.get_item(Key={'id': article["id"], 'category': article['category']})
    if 'Item' in response:
        return False
    else:
        return True    
        
        
if __name__ == "__main__":
    sample_articles = [
        {
            "id": "abc-123",
            "uri": "https://example.com/article1",
            "headline": "Sample Headline 1",
            "category": "news",
            "images": ["image1.jpg", "image2.jpg"],
            "ttl": 86400,
            "ts": "2024-04-02T12:00:00Z"
        },
        {
            "id": "abc-124",
            "uri": "https://example.com/article2",
            "headline": "Sample Headline 2",
            "category": "sports",
            "images": ["image3.jpg", "image4.jpg"],
            "ttl": 86400,
            "ts": "2024-04-02T13:00:00Z"
        },
        {
            "id": "abc-125",
            "uri": "https://example.com/article3",
            "headline": "Sample Headline 3",
            "category": "world",
            "images": [],
            "ttl": 86400,
            "ts": "2024-04-02T14:00:00Z"
        }
    ]

    event = {
        "statusCode": 200, 
        "article_blocks_json_url": "https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__www.foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJIMOJB6N5&Signature=hEYP2okJhUrIV9VkyxkmTt9I2L8%3D&Expires=1712364087",
        "article_block_tag": "<article class=\"article\">", 
        "news_site_url": "https://www.foxnews.com",
        "body": sample_articles
    }
    
    parsed_articles = lambda_handler(event=event, context=None)
    print(parsed_articles)
