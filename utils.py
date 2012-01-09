import json
import urllib2
from urlparse import urlparse
import lxml.html as l
from decorators import polite_caller

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

def hashit(obj):
    import hashlib
    m = hashlib.md5()
    m.update(json.dumps(obj))
    return m.hexdigest()
