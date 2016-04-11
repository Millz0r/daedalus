'''Utilities for analyzing document types.'''

import json

def is_json(data):
    '''Returns true if the data is json, false otherwise.'''
    try:
        json.loads(data)
    except ValueError:
        return False
    return True
