import unittest
import csv
import os
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
        filename = 'test.html'
        f = open(filename, 'w')
        message = """<html>
            <head></head>
            <body><p>Hello World!</p></body>
            </html>"""
        f.write(message)
        f.close()
        with open(filename, 'r') as content:
            self.assertEqual(souped_utf8_html.encode("utf-8"),
                             get_soup_from_html(content).encode("utf-8"))
        os.remove(filename)

    def test_is_valid_url(self):
        url_0 = "www.epocacosmeticos.com.br"
        url_1 = "/perfume"
        url_2 = "http://www.epocacosmeticos.com.br/sitemap"
        url_3 = "http://www.epocacosmeticos.com.br/buscapagina"
        url_4 = "http://www.epocacosmeticos.com.br/#item-k"
        url_5 = "http://www.epocacosmeticos.com.br/2/3/4/5"
        self.assertIs(is_valid_url(url_0), False)
        self.assertIs(is_valid_url(url_1), False)
        self.assertIs(is_valid_url(url_2), False)
        self.assertIs(is_valid_url(url_3), False)
        self.assertIs(is_valid_url(url_4), False)
        self.assertIs(is_valid_url(url_5), False)

    def test_get_canonical_url(self):
        can_url = 'https://www.google.com/recaptcha'
        self.assertEqual(can_url, get_canonical_url(can_url))


if __name__ == '__main__':
    unittest.main()
