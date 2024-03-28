# @see https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code/dynamodb/GettingStarted/scenario_getting_started_movies.py#L322

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError, ValidationError
import logging
import datetime

logger = logging.getLogger(__name__)

def remove_expired_news():
    
    try:

        dynamodb = boto3.resource(
            'dynamodb',
            region_name='ap-southeast-2',
        )

        table = dynamodb.Table("NewsArticles")  
        
        # Get current timestamp in seconds
        current_timestamp = int(datetime.datetime.now().timestamp())

        response = table.scan()        

        items = response['Items']
        
        for item in items:
            # @see https://www.bitslovers.com/crud-with-python-and-dynamodb/
            # @see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/table/delete_item.html
            ttl = item.get('ttl')
            ts = item.get('ts')
            expiration_time_stamp = ts + ttl
            if expiration_time_stamp < current_timestamp   :
                table.delete_item(
                    Key={
                        'uuid': item['uuid'],
                        'category': item['category']
                    }
        )
                

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


def lambda_handler(event: list, context: list) -> list:

    remove_expired_news()
    return {
        'statusCode': 200,
        'container_tag': event['container_tag'],
        'news_site_url': event['news_site_url']
    }

if __name__ == "__main__":
    remove_expired_news()