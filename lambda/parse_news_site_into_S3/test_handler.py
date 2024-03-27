import pytest

#from functions import get_image_path_from_S3_event
#from lambda_function import lambda_handler
#from lambda_function import extract_tag_chunks
#from lambda_function import fetch_html_from_news_site
#from lambda_function import parse_html_into_containers

@pytest.fixture
def test_data():
    return {
        'html':'<div>headline</div><article>art1</article><div>spacer</div><article tag="hello">art2</article>'
    }

'''
def test_extract_tag_chunks(test_data):
    assert 'html' in test_data
    #html = "<div>headline</div><article>art1</article><div>spacer</div><article tag='hello'>art2</article>"
    chunks = extract_tag_chunks(test_data['html'], "article")
    assert len(chunks) == 2
    assert chunks[0] == '<article>art1</article>'
    assert chunks[1] == '<article tag="hello">art2</article>'

'''
    
'''
def test_fetch_html_from_news_site(news_site_url, container_tag):
    
    news_site_url = 'https://foxnews.com'
    container_tag = "'article"
    
    news_site_html = fetch_html_from_news_site(news_site_url, container_tag)
   
    assert news_site_html != ""
'''    

'''
def test_parse_html_into_containers() ->list:

    news_site_url = 'https://foxnews.com'
    container_tag = "'article"

    news_site_html = fetch_html_from_news_site(news_site_url, container_tag)

    result = parse_html_into_containers(news_site_html, container_tag)
    
    # assert result[0] != None
'''    

    
'''
def test_lambda_function(test_data):
    event =  {
        'news_site_url':'https://foxnews.com',
        'tag':'article'
    }
    result = lambda_handler(event, None)
    
    assert 'statusCode' in result
    assert 'containers_json_url' in result
    assert 'container_tag' in result
    assert 'news_site_url' in result
    assert result['containersj_json_url'] != ''
    assert result['container_tage'] == event['container_tag']
    
'''
