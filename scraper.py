
from bs4 import BeautifulSoup
from typing import List, Dict
from foxnews import foxnews_parse_article_content
import requests

"""
# Example usage:
url = "https://example.com"
html_content = fetch_html(url)
if html_content:
    print(html_content)  # Print or use the HTML content as needed
"""

def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        html_content = response.text
        return html_content
    except requests.exceptions.RequestException as e:
        print("Error fetching HTML:", e)
        return None

def get_article_containers(url: str, tag: str) -> List[str]:
    """
    Fetches HTML content from a URL and extracts elements based on the specified tag.
    Returns a list of raw HTML strings for each found element.

    :param url: URL of the webpage to scrape.
    :param tag: The tag to search for within the HTML content.
    :return: List of raw HTML strings for each found tag.
    """
    def fetch_html(url: str) -> str:
        response = requests.get(url)
        return response.text

    html = fetch_html(url=url)
    soup = BeautifulSoup(html, features="html.parser")
    elements_raw_html = [str(element) for element in soup.find_all(tag)]
    return elements_raw_html


if __name__ == "__main__":
    
    # @see https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    foxnews_articles = get_article_containers("http://foxnews.com", tag="article")
    print(foxnews_articles)