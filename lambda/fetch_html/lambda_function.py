import requests
import json
import boto3
import re

s3_client = boto3.client('s3')


def extract_tag_chunks(text, tag):
    pattern = r"<" + tag + r".*?</" + tag + r">"
    chunks = re.findall(pattern, text, re.DOTALL)
    return chunks

def lambda_handler(event, context):
    
    url = event["url"]
    response = requests.get(event["url"])
    response.raise_for_status()  # Raise an exception for bad status codes
    html_content = response.text
    presigned_url = "";

    elements_data = extract_tag_chunks(html_content, event["tag"])
    # Convert elements_data to JSON string
    json_data = json.dumps(elements_data)

    # Convert JSON string to bytes
    data_bytes = json_data.encode('utf-8')
    
    bucket = "kdaviesnz-news-bucket"
    # Generate a unique S3 key for the HTML content
    s3_key = f'kdaviesnz.{url.replace("//", "_").replace(":", "_")}.json'

    # Upload HTML content to S3
    s3_client.put_object(Body=data_bytes, Bucket=bucket, Key=s3_key)

    # Generate a presigned URL for the S3 object
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': s3_key},
        ExpiresIn=172800  # URL expiration time (e.g., 1 hour)
    )

    return {
        'statusCode': 200,
        'presigned_url':presigned_url,
        'tag': event["tag"],
        'url': event["url"]
    }


if __name__ == "__main__":
    
    event = {
        "url":"https://foxnews.com",
        "tag":"article"
    }
    foxnews_articles = lambda_handler(event=event, context=None)
    print(foxnews_articles)