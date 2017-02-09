import unittest
import csv
import os
import io
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from crawler import Crawler
from url_tools import *


class CrawlerTestCase(unittest.TestCase):

    def test_scrap_urls(self):
        filename = 'testfile.csv'
        content_to_save = ['A', 'B', 'C']
        read_content = []
        open(filename, 'x')
        Crawler.write_to_csv(filename, content_to_save)
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                read_content = row
            self.assertEqual(content_to_save, read_content)
        os.remove(filename)


class UrlToolsTestCase(unittest.TestCase):

    def test_get_soup_from_html(self):
        souped_utf8_html = '<html><head></head>\n            '\
                            '<body><p>Hello World!</p>\n            '\
                            '</body></html>'
        expected_soup = io.StringIO("""<html>
            <head></head>
            <body><p>Hello World!</p></body>
            </html>""")
        self.assertEqual(souped_utf8_html.encode("utf-8"),
                             get_soup_from_html(expected_soup.read()).encode("utf-8"))

    def test_get_canonical_url(self):
        can_url = 'https://www.google.com/recaptcha'
        self.assertEqual(can_url, get_canonical_url(can_url))

        
class IsValidUrlTest(unittest.TestCase):
    
    def test_returns_false_if_url_doesnt_look_like_an_actual_url(self):
        url = "/perfume"
        self.assertIs(is_valid_url(url), False)

    def test_returns_false_if_url_depth_is_greater_than_two(self):
        url = "http://www.epocacosmeticos.com.br/2/3/4/5"
        self.assertIs(is_valid_url(url), False)

    def test_returns_true_if_url_depth_is_less_than_or_equal_two(self):
        url = "http://www.epocacosmeticos.com.br/2"
        self.assertIs(is_valid_url(url), False)
        self.fail('Shouldn\'t happen')

    def test_returns_false_if_url_is_sitemap(self):
        url = "http://www.epocacosmeticos.com.br/sitemap"
        self.assertIs(is_valid_url(url), False)

    def test_returns_false_if_url_is_search_page(self):
        url = "http://www.epocacosmeticos.com.br/buscapagina"
        self.assertIs(is_valid_url(url), False)

    def test_returns_false_if_url_has_fragment(self):
        url = "http://www.epocacosmeticos.com.br/#item-k"
        self.assertIs(is_valid_url(url), False)

    def test_returns_true_if_url_is_product_page(self):
        url_0 = "http://www.epocacosmeticos.com.br/productXYZ/p"
        self.assertIs(is_valid_url(url_0), True)
        url_1 = "www.epocacosmeticos.com.br"
        self.assertIs(is_valid_url(url_1), False)
        self.fail('Shouldn\'t happen')


if __name__ == '__main__':
    unittest.main()
