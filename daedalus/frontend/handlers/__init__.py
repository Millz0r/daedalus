'''Submodule that contains all of the web handlers for the application.'''

import glob
import importlib
import os.path
import re

__non_important_handlers = ['queueing_request_handler'] # pylint: disable=C0103

def __get_handler_name(handler_file_path):
    '''Gets the handlers name from the file_path.'''
    handler_file_name = os.path.basename(handler_file_path)
    match = re.match(r'(\w+_handler).py', handler_file_name)
    return match.groups(1)[0]

for file_path in glob.glob(os.path.join(os.path.dirname(__file__), '*_handler.py')):
    __handler_name = __get_handler_name(file_path)
    if __handler_name in __non_important_handlers:
        continue
    globals().update(importlib.import_module('daedalus.frontend.handlers.%s' % __handler_name).__dict__)
