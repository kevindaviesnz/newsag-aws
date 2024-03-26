import json
import boto3

def lambda_handler(event, context):
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('NewsArticles')

    # Query DynamoDB table for all items
    response = table.scan()

    # Extract the items from the response
    items = response['Items']

    # Return the items as JSON
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'  # Add CORS header for allowing requests from all origins
        },
        'body': json.dumps(items)
    }


if __name__ == "__main__":
    event = {
    }
    result = lambda_handler(event=event, context=None)
    print(result)
