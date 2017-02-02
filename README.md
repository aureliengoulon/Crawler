# Crawler


A distributed crawling app designed to scale to hundreds of processing units.
Crawler is optimized for crawling and scraping from thousands of web pages.

<img src="http://seo-advisors.com/wp-content/uploads/2013/07/Crawlers-Key-Role-Is-To-Identify-The-Right-Content-Link.jpg" alt="Img Server" width="200px"/>


## Getting Started

This is a Python program and it is supported as of version 3.6 (can also run with PyPy 3.3.5). It uses included modules and has some dependencies.

### Prerequisites

To run it, you need to install these extra modules. Makefile is here for that.
```
make -f Makefile
```

### Deploying
Run the program as a python 3 program.
```
python3 crawler.py
```

### Running the tests

All the unit tests you need to run are in unittests.py. Feel free to contribute by adding new ones or creating functional tests.
```
make test Makefile
```

### License
This project is licensed under the GNU General Public License - seet the [LICENSE](LICENSE) file for details
