import json
from sets import Set
from time import sleep
import urllib2
import datetime
from urlparse import urlparse
import lxml.html as l
import os
from xlwt import Workbook

ROOT_URL = 'http://www.kickstarter.com'

# number of seconds between downloads
POLITENESS = datetime.timedelta(seconds = 3)

# if MAX_PAGE_PARSE < 0 then it means unlimited
MAX_PAGE_PARSE = 1

EXCLUDE_NAVIGATION = Set([
    'Staff Picks',
    'Popular',
    'Recently Launched',
    'Ending Soon',
    'Small Projects',
    'Most Funded',
    'Curated Pages',
    'New York',
    'Los Angeles',
    'Brooklyn',
    'Chicago',
    'San Francisco',
    'Portland',
    'Seattle',
    'Austin',
    'Boston',
    'Nashville',
])

PROJECTS_FILE = 'projects.json'

NAVIGATION_FILE = 'navigation.json'

XL_OUTPUT_FILE = 'simple.xls'

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
    print 'Downloading {0}'.format(url)
    f = urllib2.urlopen(url).read()
    doc = l.fromstring(f)
    return doc

def extract_url(url):
    ''' Removes garbage from url
    '''
    parsed = urlparse(url)
    return '{0}://{1}{2}/'.format(parsed.scheme, parsed.netloc, parsed.path)

def to_absolute_url(url):
    ''' Converts urls like "/discover/" to "http://www.kickstarter.com/discover/"
    '''
    return extract_url('{0}{1}'.format(ROOT_URL, url))

def parse_navigation(category = None):
    start_page = get_page(to_absolute_url('/discover/'))
    nav = dict()
    for el in start_page.cssselect('.navigation > li > a'): # get first level categories
        if el.text in EXCLUDE_NAVIGATION:
            continue

        link = to_absolute_url(el.attrib['href'])
        nav[el.text] = {
            'link': link,
            'children': dict(),
        }
        category_page = get_page(link)
        for sub_el in category_page.cssselect('.subnavigation > li > a'): # look for second level categories
            if sub_el.text in EXCLUDE_NAVIGATION:
                continue

            sub_category_link = to_absolute_url(sub_el.attrib['href'])
            nav[el.text]['children'][sub_el.text] = {
                'link': sub_category_link,
            }
    return nav

navigation = dict()

# Building navigation is only done once, and then saved to navigation file
if os.path.exists(NAVIGATION_FILE): # if navigation is already built
    navigation = json.loads(open(NAVIGATION_FILE).read()) # load it
    print 'Loaded navigation!'
else:
    print 'Building navigation...'
    navigation = parse_navigation() # parse all categories
    print 'Navigation done!'
    f = open(NAVIGATION_FILE, 'w+')
    f.write(json.dumps(navigation, indent=4)) # save 'em to file

def hash(obj):
    import hashlib
    m = hashlib.md5()
    m.update(json.dumps(obj))
    return m.hexdigest()

def parse_category_by_type(category, subcategory, link, project_index, type = 'popular'):
    if subcategory:
        message = 'Parse subcategory "{0}" of "{1}"'.format(subcategory, category)
    else:
        message = 'Parse category "{0}"'.format(category)

    print message

    projects = []
    stop = False
    page_count = 1
    while not stop and (page_count <= MAX_PAGE_PARSE or MAX_PAGE_PARSE < 0):
        page = get_page('{0}{2}/?page={1}'.format(link, page_count, type))
        page_count+=1
        project_blocks = page.cssselect('.project')
        stop = len(project_blocks) == 0
        for block in project_blocks:
            try:
                location = block.cssselect('.location-name')[0].text.strip()
            except Exception:
                location = ''

            project = {
                'category': category,
                'subcategory': subcategory,
                'name': block.cssselect('.project-card > h2 > strong > a')[0].text.strip(),
                'description': block.cssselect('.project-card > p')[0].text.strip(),
                'location': location,
                'founder': block.cssselect('.project-card > h2 > span')[0].text.strip()[3:],
                'funded': None,
                'funded_date': None,
                'pledged': None,
                'days left': None,
            }
            stats = block.cssselect('.project-stats > li')
            for stat in stats:
                stat_name = ''.join(stat.xpath("text()")).strip()
                if stat_name in {'funded', 'pledged'}:
                    value = stat.cssselect('strong')[0].text.replace('%', '').replace('$', '').replace(',', '').strip()
                    project[stat_name] = float(value)
                elif stat_name == 'days left':
                    value = stat.cssselect('.num')[0].text.strip()
                    project[stat_name] = int(value)
                elif stat_name in ['hours left', 'hour left', 'min left', 'mins left']:
                    project['days left'] = 0
                else:
                    value = stat_name
                    project['days left'] = -1
                    project['funded_date'] = str(datetime.datetime.strptime(value, '%b %d, %Y'))

            h = hash(project)

            if hash not in project_index:
                project_index.add(h)
                projects.append(project)

    print '{0}. Ended!!'.format(message)
    return projects


def parse_category(category, project_index, projects_report, subcategory, subcategory_value):
    report_lines = parse_category_by_type(category, subcategory, subcategory_value['link'], project_index)
    projects_report += report_lines
    report_lines = parse_category_by_type(category, subcategory, subcategory_value['link'], project_index,
        type='successful')
    projects_report += report_lines
    return projects_report


def parse_categories(navigation):
    project_index = set()
    projects_report = []
    for category, category_value in navigation.items():
        print 'Open category "{0}"'.format(category)

        for subcategory, subcategory_value in category_value['children'].items():
            print 'Open subcategory "{0}"'.format(subcategory)
            projects_report = parse_category(
                category, project_index, projects_report, subcategory, subcategory_value
            )

        projects_report = parse_category(
            category, project_index, projects_report, category, category_value
        )

    return projects_report

# Building navigation is only done once, and then saved to navigation file
if os.path.exists(PROJECTS_FILE): # if navigation is already built
    projects = json.loads(open(PROJECTS_FILE).read()) # load it
    print 'Loaded projects!'
else:
    print 'Building projects...'
    projects = parse_categories(navigation) # parse all categories
    print 'Projects done!'
    f = open(PROJECTS_FILE, 'w+')
    f.write(json.dumps(projects, indent=4)) # save 'em to file


header = [
    'category',
    'subcategory',
    'name',
    'description',
    'location',
    'founder',
    'funded',
    'funded_date',
    'pledged',
    'days left',
]

def write_head(projects, sheet1):
    col_count = 0
    for name in header:
        sheet1.row(0).write(col_count, name)
        col_count += 1

def write_row(project, row_count, sheet1):
    col_count = 0
    for name in header:
        sheet1.row(row_count).write(col_count, project[name])
        col_count += 1

def output_xl(projects):
    book = Workbook()
    sheet = book.add_sheet('Sheet')
    write_head(projects, sheet)
    row_count = 1
    for project in projects:
        write_row(project, row_count, sheet)
        row_count += 1
    sheet.flush_row_data()
    book.save(XL_OUTPUT_FILE)

output_xl(projects)
