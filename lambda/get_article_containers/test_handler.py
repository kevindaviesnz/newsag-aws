# This file: lambda/get_article_containers/test_handler.py
# pip install requests --target .
import pytest

from lambda_function import fetch_html_from_presigned_url
from lambda_function import lambda_handler

@pytest.fixture
def test_data():
    return {
        'event': {
            "presigned_url":"https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJM3V6Q2HU&Signature=VjtNNUSaPPVJG0XyxygUIMxnJQU%3D&Expires=1711854291",
            "tag": "article",
            "url": "https://foxnews.com"       
        }
    }
    
def test_fetch_html_from_presigned_url():
    event = {
        "presigned_url":"https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJM3V6Q2HU&Signature=VjtNNUSaPPVJG0XyxygUIMxnJQU%3D&Expires=1711854291",
        "tag": "article",
        "url": "https://foxnews.com"       
    }
    fetch_html_from_presigned_url(event['presigned_url'])

'''
def test_lambda_function():
    event = {
        "presigned_url":"https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJM3V6Q2HU&Signature=VjtNNUSaPPVJG0XyxygUIMxnJQU%3D&Expires=1711854291",
        "tag": "article",
        "url": "https://foxnews.com"       
    }


'''




