import json
from time import sleep
import urllib2
import datetime
import lxml.html as l
import os

ROOT_URL = 'http://www.kickstarter.com'
POLITENESS = datetime.timedelta(seconds = 3)


def polite_caller(func):
    ''' Due to banning policies we must restrict downloading more then one page per POLITENESS period
    '''
    polite_caller.last_called = datetime.datetime.now()
    def polite_wrapper(*args, **kwargs):
        polite_interval = POLITENESS - (datetime.datetime.now() - polite_caller.last_called)
        sleep(polite_interval.seconds)
        result = func(*args, **kwargs)
        polite_caller.last_called = datetime.datetime.now()
        return result
    return polite_wrapper


@polite_caller
def get_page(url):
    ''' Downloads and parses page
    '''
    f = urllib2.urlopen(url).read()
    doc = l.fromstring(f)
    return doc

def to_absolute_url(url):
    ''' Converts urls like "/discover/" to "http://www.kickstarter.com/discover/"
    '''
    return '{0}{1}'.format(ROOT_URL, url)

def parse_navigation(category = None):
    doc = get_page(to_absolute_url('/discover/'))
    nav = {}
    for el in doc.cssselect('.navigation > li > a'): # get first level categories
        link = to_absolute_url(el.attrib['href'])
        nav[el.text] = {
            'link': link,
            'children': {},
        }
        doc = get_page(link)
        for sub_el in doc.cssselect('.subnavigation > li > a'): # look for second level categories
            sub_category_link = to_absolute_url(sub_el.attrib['href'])
            nav[el.text]['children'][sub_el.text] = {
                'link': sub_category_link,
            }
    return nav

navigation = {}

navigation_file = 'navigation.json'
# Building navigation is only done once, and then saved to navigation file
if os.path.exists(navigation_file): # if navigation is already built
    navigation = json.loads(open(navigation_file).read()) # load it
else:
    navigation = parse_navigation() # parse all categories
    f = open(navigation_file, 'w+')
    f.write(json.dumps(navigation, indent=4)) # save 'em to file

