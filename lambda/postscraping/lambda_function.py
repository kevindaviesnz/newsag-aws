import logging
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError, ValidationError
import json

logger = logging.getLogger(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('NewsArticles') 

def lambda_handler(event, context):
    try:
        articles = json.loads(event['body'])  # Parse JSON string to Python object
        filtered_articles = list(filter(filter_existing_articles, articles))
        return filtered_articles
    except (ValidationError, ClientError) as err:
        logger.error(
            "Error occurred: %s: %s", 
            err.response["Error"]["Code"], 
            err.response["Error"]["Message"]
        )
        raise

def filter_existing_articles(article):
    response = table.get_item(Key={'id': article["id"], 'category': article['category']})
    return 'Item' not in response

if __name__ == "__main__":
    event = {
        "statusCode": 200,
        "body": "[{\"uri\": \"https://www.foxnews.com/politics/desantis-notches-win-lawsuit-migrant-flights-but-company-arranged-them-not-clear-yet\",\"headline\": \"Judge hands DeSantis major win in lawsuit over migrant flights to lux progressive vacation spot\", \"category\": \"politics\", \"images\": [\"http://a57.foxnews.com/prod-hp.foxnews.com/images/2024/04/720/405/8ee77673ac60dbf0a49c5c68bbae235e.jpg?tl=1&ve=1\"], \"ttl\": 86400, \"ts\": 1712022321, \"id\": \"dfdcf94b792aee172710f152205b8828e79d2e44bbc2f207b62735dfe4410cce\"}]",
        "article_block_tag": "<article class=\"article\">",
        "news_site_url": "https://www.foxnews.com"
    }
    parsed_articles = lambda_handler(event=event, context=None)
    print(parsed_articles)
