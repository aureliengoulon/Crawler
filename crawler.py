import csv
import sys
import time
import multiprocessing as mp
from multiprocessing import Manager
from multiprocessing.sharedctypes import Value
from urllib.parse import urljoin, urlparse
from url_tools import *


class Crawler(mp.Process):

    def __init__(self, task_q, result_l, task_lock, result_lock, csv_lock,
                 found, base_url, css_selectors, csv_filename, csv_headers,
                 headers):
        mp.Process.__init__(self)
        self.task_q = task_q
        self.result_l = result_l
        self.task_lock = task_lock
        self.result_lock = result_lock
        self.csv_lock = csv_lock
        self.found = found
        self.base_url = base_url
        self.css_selectors = css_selectors
        self.csv_filename = csv_filename
        self.csv_headers = csv_headers
        self.headers = headers

    def run(self):
        """Overrides multiprocessing.Process.run()"""
        while True:
            new_urls = []
            url_to_parse = ''
            with self.task_lock:
                url_to_parse = self.task_q.get()
                # Scrapping URLs from page
            html_url_soup = get_soup_from_html(
                get_html_from_url(url_to_parse, self.headers))
            new_urls = self.scrap_urls(html_url_soup)
            for link in new_urls:
                # Check we are on a valid product page
                splited_path = urlparse(link).path.split('/')
                if len(splited_path) == 3 and splited_path[2] == 'p':
                    # Scrapping product infos from page
                    html_info_soup = get_soup_from_html(
                                get_html_from_url(link, self.headers))
                    content_to_save = []
                    for item in html_info_soup.select(self.css_selectors):
                        content_to_save.append(item.text)
                    if len(content_to_save) == 2:
                        content_to_save.append(get_canonical_url(link))
                        # Write to csv here
                        with self.csv_lock:
                            self.write_to_csv(self.csv_filename,
                                              content_to_save,
                                              self.csv_headers)
                            self.found.value += 1

                    # Look if there is any new URLs
                    self.scrap_urls(html_info_soup)
            # Notifying the queue we are done with this task
            self.task_q.task_done()
        return

    def scrap_urls(self, soup):
        """Return a list of unbrowsed URLs
        Will also put every unbrowsed URL in the queue of URL to browse
        and discard do nothing with it if already in visited history.
        """
        new_urls = []
        for tag in soup.findAll('a', href=True):
            tag['href'] = urljoin(self.base_url, tag['href'])
            with self.result_lock:
                if is_valid_url(tag['href']) and \
                    self.base_url in tag['href'] and \
                        tag['href'] not in self.result_l:
                    # Proc_name :: total_urls  new_urls  URL
                    print('{:11s} :: {:6d} {:5d}  {}'.format(
                          self.name, len(self.result_l), self.found.value,
                          urlparse(tag['href']).path))

                    new_urls.append(tag['href'])
                    self.result_l.append(tag['href'])
                    self.task_q.put(tag['href'])
        return new_urls

    @staticmethod
    def write_to_csv(filename, content_to_save, file_headers=[]):
        """Create a new file if not already done before.
        Appends the specified line of content into a new row of the file
        """
        if os.path.isfile(filename):
            with open(filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(content_to_save)
        else:
            with open(filename, 'w+') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(file_headers)
                writer.writerow(content_to_save)


def check_duplicate(filename):
    f1 = csv.reader(open(filename, 'r'))
    newrows = []
    for row in f1:
        if row not in newrows:
            newrows.append(row)
        writer = csv.writer(open('.tmp.csv', 'w'))
        writer.writerows(newrows)

    os.remove(filename)
    os.rename('.tmp.csv', filename)


def main():
    try:
        # Establish communication queues
        # Object available through a manager allow for distributed processing
        manager = Manager()
        crawl_queue = manager.JoinableQueue()
        crawled_list = manager.list()
        # Represents the actual number of parsed product pages
        found = manager.Value('i', 0, lock=True)

        # All locks will be passed to child processes, avoiding parent proc GC
        crawl_lock = manager.Lock()
        crawled_lock = manager.Lock()
        csv_lock = manager.Lock()

        base_url = "http://www.epocacosmeticos.com.br"
        css_selectors = 'div.productName, title'
        csv_filename = 'epocacosmeticos.csv'
        csv_headers = ['Nome', 'Titulo', 'URL']
        headers = {'User-Agent': 'Pipocabot/4.2 \
                    (+http://www.pipoca.le/bot.html)'}
        open(csv_filename, 'w+')
        os.remove(csv_filename)
        # Start consumers
        num_consumers = mp.cpu_count() * 4

        print('Creating {} crawlers'.format(num_consumers))
        start_time = time.time()
        # Instantiate new consumers
        crawlers = [Crawler(crawl_queue, crawled_list, crawl_lock,
                    crawled_lock, csv_lock, found, base_url,
                    css_selectors, csv_filename, csv_headers, headers)
                    for i in range(num_consumers)]

        # Enqueue job (url to crawl)
        crawl_queue.put(base_url)
        crawled_list.append(base_url)

        for w in crawlers:
            w.start()

        # Wait for all of the tasks to be done (making sure all
        # items in crawl queue have been gotten and processed)
        crawl_queue.join()
        print("queue joined")

        print('\nwriting to {}\n'.format(csv_filename))

        # print("\nresults\n")
        # print(crawled_list)

        # Crawlers shouldn't be stay in a blocked state that long
        # My solution is to terminate them. I investigated this
        # matter for some time now. Recommend finding another way.
        # Pool of processes didn't seem fit as size of site is unknown
        for w in crawlers:
            w.join(1)
            # Join time out
            if w.is_alive():
                w.terminate()

    except KeyboardInterrupt:
        print(' while crawling, terminating crawlers')
        print("Shutdown requested...exiting")
        for w in crawlers:
            w.terminate()
        print('all crawlers terminated')
        delete = input("Delete csv result file? (y/n): ")
        try:
            if delete == 'y':
                os.remove(csv_filename)
            else:
                print("{} might be corrupted".format(csv_filename))

        except FileNotFoundError:
            print("File not found")

    except Exception as e:
        print('got exception: {}, terminating the pool'.format(e))
        for w in crawlers:
            w.terminate()
        print('all crawlers terminated')
        os.remove(csv_filename)

    else:
        try:
            check_duplicate(csv_filename)
            print('\n --- Exiting --- \n\nCheck results in {}'.format(
                csv_filename))

        except FileNotFoundError:
            print("File not found")

    finally:
        
        print("--- finished at {} ---".format(time.strftime(
            "%H:%M:%S", time.localtime())))
        print("--- {} sec ---".format(time.time() - start_time))

        sys.exit(0)


if __name__ == '__main__':
    main()
