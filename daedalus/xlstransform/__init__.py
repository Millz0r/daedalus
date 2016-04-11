'''
xlstransform - Document transformation module. This module is the heart of the documentation
translation service for the daedalus project. Right now it can convert between json and excel.
More formats will be added when there is a need.
'''

from daedalus.xlstransform.utils import is_json
from daedalus.xlstransform.transforms import transform

__all__ = ['is_json', 'transform']

