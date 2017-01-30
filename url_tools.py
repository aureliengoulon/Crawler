import os
import requests
import validators
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def is_valid_url(url):
    '''Check URL validity against known unviable locators'''
    # [0] / [1] / [2] / [3] ... with [0]=='' before netloc
    allowed_depth = 2
    if not validators.url(url):
        return False
    else:
        parsed_url = urlparse(url)
        if len(parsed_url.path.split('/')) - 1 > allowed_depth or \
            url == "http://www.epocacosmeticos.com.br/sitemap" or \
                parsed_url.path == '/buscapagina' or \
                parsed_url.path == '/busca' or \
                parsed_url.fragment != '':
            return False
        else:
            return True


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


def get_soup_from_html(htmltext):
    '''Transform HTML text into a soup parseable object'''
    return BeautifulSoup(htmltext, "lxml")


def get_canonical_url(url):
    '''Returns canonical URL from link (protocol, name and location)'''
    #return BeautifulSoup(htmltext, "lxml")
    return BeautifulSoup(htmltext, "html5lib")

