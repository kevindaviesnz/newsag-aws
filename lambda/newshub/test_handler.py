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

    }
    result = lambda_handler(event, None)
#    assert 'statusCode' in result

