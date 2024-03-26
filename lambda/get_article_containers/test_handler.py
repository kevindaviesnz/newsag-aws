# This file: lambda/get_article_containers/test_handler.py
import pytest

#from functions import get_image_path_from_S3_event
from lambda_function import fetch_html_from_presigned_url
from lambda_function import lambda_handler

@pytest.fixture
def test_data():
    return {
    }

    
def test_lambda_fetch_html_from_presigned_url(test_data):
    event = {
        "presigned_url":"https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJM3V6Q2HU&Signature=VjtNNUSaPPVJG0XyxygUIMxnJQU%3D&Expires=1711854291",
        "tag": "article",
        "url": "https://foxnews.com"       
    }
    presigned_url_html_content = fetch_html_from_presigned_url(event['presigned_url'])
    '''
    result = lambda_handler(event, None)
    assert 'statusCode' in result
    assert 'articles_url' in result
    assert 'tag' in result
    assert 'tag' in result
    assert 'url' in result
    assert result['url'] == event['url']
    assert result['articles_url'] != ''
    '''