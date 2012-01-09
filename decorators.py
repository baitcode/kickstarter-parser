import json
from time import sleep
import os
from settings import *


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


def cache_to_file(file_path, obj_name = 'object'):
    def decorator(func):
        def wrapper(*args, **kwargs):
            file_path = os.path.join(RESOURCES_DIR, wrapper.file_path)

            if not os.path.exists(RESOURCES_DIR):
                os.mkdir(RESOURCES_DIR)

            if os.path.exists(file_path):
                obj = json.loads(open(file_path).read())
                print 'Loaded {0}!'.format(obj_name)
            else:
                print 'Building {0}...'.format(obj_name)
                obj = func(*args, **kwargs)
                print '{0} done!'.format(obj_name)
                f = open(file_path, 'w+')
                f.write(json.dumps(obj, indent=4))
            return obj
        wrapper.file_path = file_path
        return wrapper

    return decorator
