import os
import requests
import validators
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def is_valid_url(url):
    '''Check URL validity against known unviable locators'''
    MAX_URL_DEPTH = 2
    parsed_url = urlparse(url)
    checks = {
        'looks_like_url': validators.url(url),
        'within_depth_limit': len(parsed_url.path.split('/')) - 1 <= MAX_URL_DEPTH,
        'is_not_sitemap': url != 'http://www.epocacosmeticos.com.br/sitemap',
        'is_not_search_page': parsed_url.path not in {'/busca', '/buscapagina'},
        'doesnt_have_fragment': not parsed_url.fragment,
    }.values()
    
    return True if all(checks) else False

def is_product_url(url):
    '''Check if URL is a product page'''
    splited_path = urlparse(link).path.split('/')
    if len(splited_path) == 3 and splited_path[2] == 'p':
        return True
    else
        False

def get_html_from_url(url, headers={}):
    '''Fetch html content from url with HTTP code 200 OK'''
    htmltext = ''
    if is_valid_url(url):
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except ConnectionError:
            print("Network problem: [out of reach] {}".format(url))
        except HTTPError:
            print("HTTP Error: [nsuccessfull access] {}".format(url))
        except TooManyRedirects:
            print("Redirection: [too many redirect] {}".format(url))
        else:
            # everything is fine
            if response.status_code == 200:
                if response.headers[
                  'content-type'].split(';')[0] == 'text/html':
                    htmltext = response.text
    return htmltext


def get_soup_from_html(url, headers):
    '''Transform HTML text into a soup parseable object'''
    return BeautifulSoup(get_html_from_url(url, headers), "html5lib")


def get_canonical_url(url):
    '''Returns canonical URL from link (protocol, name and location)'''
    return urlparse(url).scheme+'://'+urlparse(url).netloc+urlparse(url).path
