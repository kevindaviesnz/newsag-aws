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
            'ttl': 86400,  # 24 hours
        }


        # Find picture and img tags
        picture_tag = soup.find('picture')
        if picture_tag:
            image_tag = picture_tag.find('img')
            src = image_tag.get('data-src') if image_tag else None
            article_container["images"] = [f"http:{src}"] if src else []

        return article_container
    else:
        return None

def lambda_handler(event, context):
    
    # url to json file to parse
    response = requests.get(event["presigned_url"])
    response.raise_for_status()  # Raise an exception for HTTP error responses
    articles_json = response.json()  # This method parses the JSON response into a Python dict or list
    parsed_articles_json = list(map(foxnews_parse_article_content, articles_json[:10]))
    json_data = json.dumps(parsed_articles_json)
    # Store articles in a bucket
    bucket = "kdaviesnz-news-bucket"

    # Convert JSON string to bytes
    data_bytes = json_data.encode('utf-8')

    # Generate a unique S3 key for the articles
    s3_key = f'kdaviesnz.foxnews.json'

    # Upload json content to S3
    s3_client.put_object(Body=data_bytes, Bucket=bucket, Key=s3_key)
    
    # Generate a presigned URL for the S3 object
    parsed_articles_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': s3_key},
        ExpiresIn=172800  # URL expiration time (e.g., 1 hour)
    )
    
    # s3://kdaviesnz-news-bucket/kdaviesnz.foxnews.json
    return {
        'statusCode': 200,
        'bucket_name': bucket,
        'parsed_articles_url': parsed_articles_url,
        'uuid':  str(uuid.uuid4()),
        's3_object_key': 'kdaviesnz.foxnews.json'
    }


if __name__ == "__main__":
    event = {
        "presigned_url":"https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJM3V6Q2HU&Signature=iNC0%2BnQUfahKObCLS1x440T%2BySc%3D&Expires=1710880508",
        "tag": "article"        
    }
    parsed_articles = lambda_handler(event=event, context=None)
    print(parsed_articles)
