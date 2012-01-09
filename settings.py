# number of seconds between downloads
import datetime

POLITENESS = datetime.timedelta(seconds = 3)

# if MAX_PAGE_PARSE < 0 then it means unlimited
MAX_PAGE_PARSE = 1

EXCLUDE_NAVIGATION = set([
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

RESOURCES_DIR = 'resources'

COLUMNS = [
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
