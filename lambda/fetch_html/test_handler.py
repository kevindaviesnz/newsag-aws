import pytest

#from functions import get_image_path_from_S3_event
from lambda_function import lambda_handler
from lambda_function import extract_tag_chunks

@pytest.fixture
def test_data():
    return {
        'html':'<div>headline</div><article>art1</article><div>spacer</div><article tag="hello">art2</article>'
    }

def test_extract_tag_chunks(test_data):
    assert 'html' in test_data
    #html = "<div>headline</div><article>art1</article><div>spacer</div><article tag='hello'>art2</article>"
    chunks = extract_tag_chunks(test_data['html'], "article")
    assert len(chunks) == 2
    assert chunks[0] == '<article>art1</article>'
    assert chunks[1] == '<article tag="hello">art2</article>'
    
def test_lambda_function(test_data):
    event =  {
        'url':'https://foxnews.com',
        'tag':'article'
    }
    result = lambda_handler(event, None)
    assert 'statusCode' in result
    assert 'presigned_url' in result
    assert 'tag' in result
    assert 'tag' in result
    assert 'url' in result
    assert result['url'] == event['url']
    assert result['presigned_url'] != ''