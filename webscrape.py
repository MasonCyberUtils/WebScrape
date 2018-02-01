from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import os
import time
import sys


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of resoinse is some kind of HTML/XML, return the
    text content, otherwise return None"""
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns true if response seems to be HTML, false otherwise
    :param resp:
    :return:
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    print(e)


def get_data():
    """
    Downloads the page where the list of data is found
    and returns a list of strings, one per data item
    :return:
    """
    url = input("Please enter full url of data source:\n>> ")

    response = simple_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        names = set()
        html_tag = input("Enter HTML tag to select:\n>> ")
        for html_tag in html.select(html_tag):
            for name in html_tag.text.split('\n'):
                if len(name) > 0:
                    names.add(name.strip())
        return list(names)

    # Raise exception if failed to get data from url
    raise Exception('Error retrieving contents at {}'.format(url))


def local_get_data():
    """
    Just like get_names() only local
    """
    url = input("Please enter full file path of data source:\n>> ")

    raw_html = open(url).read()
    html = BeautifulSoup(raw_html, 'html.parser')
    names = set()
    html_tag = input("Enter HTML tag to select:\n>> ")
    for html_tag in html.select(html_tag):
        for name in html_tag.text.split('\n'):
            if len(name) > 0:
                names.add(name.strip())
    return list(names)


def get_hits_on_data(name):
    """
    Accepts a `name` of data and returns the number of hits
    that data has on wikipedia (or your site of choice) in the last
    60 days, as an `int`
    """
    url_root = 'https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/{}'
    response = simple_get(url_root.format(name))

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')

        hit_link = [a for a in html.select('a')
                    if a['href'].find('latest-60') > -1]
        if len(hit_link) > 0:
            # Strip commas:
            link_text = hit_link[0].text.replace(',','')
            try:
                # Convert to int
                return int(link_text)
            except:
                log_error("Couldn't parse {} as an `int`".format(link_text))

    log_error('No page views found for {}'.format(name))
    return None


if __name__ == '__main__':
    running = True
    os.system('clear')
    print("Welcome to WebScrape!")
    print("---"*20)
    print("WebScrape is a command line utility written purely in Python designed to grab an HTML page\n"
          " and the data contained in HTML tags (of which you specify).\n After grabbing this data, "
          "WebScrape will then get the number of\n `hits` your data has gotten on Wikipedia.\n")
    time.sleep(3)
    while(True):
        print("==="*20)
        print("WebScrape")
        print("==="*20)
        data_location = int(input("Please choose your data source:\n1) Website\n2) Local File\n3) Quit ScrapeMe\n>> "))
        if data_location == 1:
            names = get_data()
            print('Gathering data...\n')
            print('... done.\n')
        elif data_location == 2:
            names = local_get_data()
            print('Gathering data...\n')
            print('... done.\n')
        elif data_location == 3:
            sys.exit(0)

        results = []

        length_of_list = int(input("How many data points would you like to return? Enter [999999] for all items.\n>> "))

        print("Getting stats for each data item...")
        for name in names:
            try:
                hits = get_hits_on_data(name)
                if hits is None:
                    hits = -1
                results.append((hits, name))
            except:
                results.append((-1, name))
                log_error('error encountered while processing '
                          '{}, skipping'.format(name))
        print('... done.\n')

        results.sort()
        results.reverse()

        if len(results) > length_of_list:
            top_marks = results[:length_of_list]
        else:
            top_marks = results

        print('\nThe most popular data objects from your query are:\n')
        for (mark, data) in top_marks:
            print('{} with {} page views'.format(data, mark))

        no_results = len([res for res in results if res[0] == -1])
        print('\nI could not locate results for '
              '{} data objects on the list'.format(no_results))

        input("Press [Return/Enter] to continue...")


