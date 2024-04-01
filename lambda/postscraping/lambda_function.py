import logging
import json
import boto3


logger = logging.getLogger(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('your_table_name') 

def lambda_handler(event, context):
    
    try:
        
        articles = json.loads(event['body'])
        
        # Filter out articles that already exist in DynamoDB
        filtered_articles = list(filter(filter_existing_articles, articles))

        # We will be passing the articles directly to DynamoDB via state machine
        return filtered_articles
        
        pass

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
      
        
def filter_existing_articles(article):
    
    # Check if a matching record exists in DynamoDB
    # "id" is the partition key and is a hash of the article.
    response = table.get_item(
        Key={
            'id': article["id"]  
        }
    )

    # If a matching record exists in DynamoDB, filter it out
    if 'Item' in response:
        return False
    else:
        return True    
        
        
if __name__ == "__main__":
    event = {
        "statusCode": 200, 
        "article_blocks_json_url": "https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__www.foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJIMOJB6N5&Signature=hEYP2okJhUrIV9VkyxkmTt9I2L8%3D&Expires=1712364087",
        "article_block_tag": "<article class=\"article\">", 
        "news_site_url": "https://www.foxnews.com"
    }
    parsed_articles = lambda_handler(event=event, context=None)
    print(parsed_articles)