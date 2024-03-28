import pytest

from lambda_function import foxnews_parse_article_content
from lambda_function import lambda_handler

@pytest.fixture
def test_data():
    return {
        'html':'<div>headline</div><article>art1</article><div>spacer</div><article tag="hello">art2</article>'
    }

def test_foxnews_parse_article_content():
    article_element = ""
    foxnews_parse_article_content(article_element)
    pass

def test_lambda_handler(test_data):
    event =  {
        "containers_json_url":"https://kdaviesnz-news-bucket.s3.amazonaws.com/kdaviesnz.https__foxnews.com.json?AWSAccessKeyId=AKIA42RD47OJM3V6Q2HU&Signature=bm9CN7GsuUmb0M6VrQWdjiVysCI%3D&Expires=1711163704",
        "container_tag": "article" 
    }
    result = lambda_handler(event, None)
#    assert 'statusCode' in result

