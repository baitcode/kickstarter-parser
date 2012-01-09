# How to use

To run, run parser.py

Navigation is created once, and stored in NAVIGATION_FILE, to recreaate navigation - delete file. Same is with projects.

# Settings reference

* *POLITENESS* - number of seconds between downloads (example: 3)
* MAX_PAGE_PARSE - maximum number of page that should be parsed during project lookup (example: 1)
* EXCLUDE_NAVIGATION - set of menu titles to exclude from parsing ( exaple: set(['Staff Picks', 'Popular', 'Recently Launched',]) )
* PROJECTS_FILE - cache file for project gathered (example: projects.json)
* NAVIGATION_FILE - cache file for navigation info (example: navigation.json)
* XL_OUTPUT_FILE - Excel report file name (example: zzz.xls)
* RESOURCES_DIR - cache dir (example: olololol)
* COLUMNS - Excel report columns in that order, possible values:
    ['category', 'subcategory', 'name', 'description', 'location', 'founder', 'funded', 'funded_date', 'pledged', 'days left',]
