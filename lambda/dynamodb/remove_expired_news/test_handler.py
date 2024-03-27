import pytest

from lambda_function import remove_expired_news

@pytest.fixture
def test_data():
    return {

    }
    
def test_remove_expired_news():
    remove_expired_news()
    pass
    
def test_lambda_handler():
    test_remove_expired_news()    

    pass