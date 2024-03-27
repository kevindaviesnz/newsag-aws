# @see https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code/dynamodb/GettingStarted/scenario_getting_started_movies.py#L322

import boto3
from botocore.exceptions import ClientError

def remove_expired_news():
    
    #"doc-example-table-movies", "moviedata.json", boto3.resource("dynamodb")
    dyn_resource = boto3.resource("dynamodb")
    table = dyn_resource.Table('NewsArticles')
    table.load()
    
    try:
        
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('ttl').eq('86400')
        )
        
        items = response['Items']
        for item in items:
            table.delete_item(Key={'uuid': item['uuid']})
            pass
        
    except ClientError as err:
        raise
    


def lambda_handler(event: list, context: list) -> list:
    pass