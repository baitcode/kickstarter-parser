import os
from xlwt import Workbook
from decorators import cache_to_file
from settings import *
from utils import extract_url, get_page, hashit

ROOT_URL = 'http://www.kickstarter.com'

def to_absolute_url(url):
    ''' Converts urls like "/discover/" to "http://www.kickstarter.com/discover/"
    '''
    return extract_url('{0}{1}'.format(ROOT_URL, url))

@cache_to_file(NAVIGATION_FILE, 'navigation')
def parse_navigation():
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

def parse_category(category, project_index, projects_report, subcategory, subcategory_value):
    report_lines = parse_category_by_type(category, subcategory, subcategory_value['link'], project_index)
    projects_report += report_lines
    report_lines = parse_category_by_type(category, subcategory, subcategory_value['link'], project_index,
        type='successful')
    projects_report += report_lines
    return projects_report

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

            h = hashit(project)

            if h not in project_index:
                project_index.add(h)
                projects.append(project)

    print '{0}. Ended!!'.format(message)
    return projects



@cache_to_file(PROJECTS_FILE, 'projects')
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


def write_head(sheet):
    col_count = 0
    for name in COLUMNS:
        sheet.row(0).write(col_count, name)
        col_count += 1

def write_row(project, row_count, sheet1):
    col_count = 0
    for name in COLUMNS:
        sheet1.row(row_count).write(col_count, project[name])
        col_count += 1

def output_xl(projects):
    book = Workbook()
    sheet = book.add_sheet('Sheet')
    write_head(sheet)
    row_count = 1
    for project in projects:
        write_row(project, row_count, sheet)
        row_count += 1
    sheet.flush_row_data()
    book.save(XL_OUTPUT_FILE)

navigation = parse_navigation() # parse all categories
projects = parse_categories(navigation) # parse all categories
output_xl(projects)
