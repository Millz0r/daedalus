# pylint: disable=anomalous-backslash-in-string
'''This module contains agnostic validation functions.'''

import re

from datetime import datetime
from xlrd import xldate_as_tuple

# Enum values used in the spreadsheet.
_LEASING_STATUS = [u'LEASED', u'LEASED - M2M', u'RENO', u'REHAB', u'VACANT - ADVERT', u'VACANT - PENDING', u'VACANT - TRANSITION', u'N/A']
_CLASS_OF_SPACE = [u'A', u'B', u'C']
_OWNER_ESTIMATE_SOURCES = [u'INTERNAL AVM', u'EXTERNAL BPO', u'N/A']
_US_STATES_SHORT = [u'AL', u'AK', u'AZ', u'AR', u'AS', u'CA', u'CO', u'CT', u'DC', u'DE', u'FL', u'GA', u'GU', u'HI', u'ID', u'IL', u'IN', u'IA',
                    u'KS', u'KY', u'LA', u'ME', u'MD', u'MA', u'MI', u'MN', u'MP', u'MS', u'MO', u'MT', u'NE', u'NV', u'NH', u'NJ', u'NM', u'NY', u'NC',
                    u'ND', u'OH', u'OK', u'OR', u'PA', u'PR', u'RI', u'SC', u'SD', u'TN', u'TX', u'UT', u'VT', u'VA', u'VI', u'WA', u'WV', u'WI', u'WY']
_US_STATES_LONG = [u'ALASKA', u'ALABAMA', u'ARKANSAS', u'AMERICAN SAMOA', u'ARIZONA', u'CALIFORNIA', u'COLORADO', u'CONNECTICUT', u'DISTRICT OF COLUMBIA',
                   u'DELAWARE', u'FLORIDA', u'GEORGIA', u'GUAM', u'HAWAII', u'IOWA', u'IDAHO', u'ILLINOIS', u'INDIANA', u'KANSAS', u'KENTUCKY', u'LOUISIANA',
                   u'MASSACHUSETTS', u'MARYLAND', u'MAINE', u'MICHIGAN', u'MINNESOTA', u'MISSOURI', u'NORTHERN MARIANA ISLANDS', u'MISSISSIPPI', u'MONTANA',
                   u'NATIONAL', u'NORTH CAROLINA', u'NORTH DAKOTA', u'NEBRASKA', u'NEW HAMPSHIRE', u'NEW JERSEY', u'NEW MEXICO', u'NEVADA', u'NEW YORK',
                   u'OHIO', u'OKLAHOMA', u'OREGON', u'PENNSYLVANIA', u'PUERTO RICO', u'RHODE ISLAND', u'SOUTH CAROLINA', u'SOUTH DAKOTA' 'TENNESSEE', u'TEXAS',
                   u'UTAH', u'VIRGINIA', u'VIRGIN ISLANDS', u'VERMONT', u'WASHINGTON', u'WISCONSIN', u'WEST VIRGINIA', u'WYOMING']


def _check_regex_field(regex, field):
    '''Check if specified regex matches given field.'''
    regex_object = re.compile(regex)
    # Need to stringify the field, because it might be a number.
    result = re.match(regex_object, str(field))
    if not result:
        return (False, 'Invalid character or format.')
    return (True, None)


# Cell type validation functions.
def valid_date(field):
    '''Check for a valid date field.'''
    # Excel uses floats for storing dates. If that alone wasn't a bad idea, there are two base date systems. We assume we are using the default, 1900-one here.
    # xlrd module provides this handy snippet for transforming dates. Rely on it for correctness.
    try:
        xldate_as_tuple(field, 0)
    except ValueError:
        # Try parsing it directly using datetime.strptime instead.
        date_formats = ['%d/%m/%Y', '%d/%b/%Y', '%Y/%m/%d', '%Y/%b/%d', '%d-%m-%Y', '%d-%b-%Y', '%Y-%m-%d', '%Y-%b-%d']
        for date_format in date_formats:
            try:
                datetime.strptime(field, date_format)
                return (True, None)
            except ValueError:
                pass
        return (False, 'Invalid date.')
    return (True, None)


def valid_percentage(field, precision=None):
    '''Check for a valid percentage field.'''
    # Eg. 8.00%, 8%, 0.08
    try:
        value = float(field)
    except ValueError:
        # Due to formatting issues need to concatenate %$ separately.
        percentage_regex = ('^\d+\.\d{%d}' % precision + '%$') if precision else '^\d+(.\d+)?%$'
        result, errors = _check_regex_field(percentage_regex, field)
        if not result:
            return (False, errors)
        value = float(field[:-1])
    # Check for 0-100 bounds.
    if not 0.0 <= value <= 100.0:
        return (False, 'Percentage outside 0-100 bounds.')
    return (True, None)


def valid_dollar(field, precision=None):
    '''Check for a valid dollar field.'''
    # Eg. $3,950, $3,950.00, 3950.0
    try:
        float(field)
    except ValueError:
        value = field
        # Check for valid currency mark.
        if field.startswith('$'):
            value = field[1:]
        elif field.endswith('USD'):
            value = field[:-3]
        # Replace kilo delimiters.
        value = value.replace(',', '')
        # Try to convert it again without all the extra chars.
        try:
            float(value)
        except ValueError:
            return (False, 'Invalid dollar value.')
        if precision is not None:
            dollar_regex = '^\d+(\.\d{%d})$' % precision
            result, _ = _check_regex_field(dollar_regex, value)
            if not result:
                return (False, 'Invalid precision.')
    return (True, None)


def valid_year(field):
    '''Check if year built field is valid.'''
    # Excel saves most numbers as float, try to check that too.
    # Eg. 2001, 2001.0
    year_regex = '^\d{4}(.0)?$'
    return _check_regex_field(year_regex, field)


def valid_address(field):
    '''Check if address field is valid.'''
    # Eg. 789 Main Str Unit C
    address_regex = '^[ ]*\w[ \-,\'\w]+$'
    return _check_regex_field(address_regex, field)


def valid_city(field):
    '''Check if city field is valid.'''
    # Eg. New Reno
    city_regex = '^[ \-\'\w]+$'
    return _check_regex_field(city_regex, field)


def valid_county(field):
    '''Check if county field is valid.'''
    # Eg. McPherson County
    county_regex = '^[ \-\'\w]+$'
    return _check_regex_field(county_regex, field)


def valid_zip_code(field):
    '''Check if ZIP code field is valid.'''
    # Excel saves most numbers as float, try to check that too.
    # Eg. 56789, 56789.0, 45562-2544
    zip_regex = '^\d{5}((.0)?|(-\d{4}))?$'
    return _check_regex_field(zip_regex, field)


def valid_us_state(field):
    '''Check for a valid enum in a state field.'''
    if field.upper() not in _US_STATES_SHORT and field.upper() not in _US_STATES_LONG:
        return (False, 'No such US state: %s.' % field)
    return (True, None)


def valid_estimate_source(field):
    '''Check for a valid enum in a owner estimate source field.'''
    if field.upper() not in _OWNER_ESTIMATE_SOURCES:
        return (False, 'No such owner estimate source: %s.' % field)
    return (True, None)


def valid_leasing_status(field):
    '''Check for a valid enum in a leasing status field.'''
    if field.upper() not in _LEASING_STATUS:
        return (False, 'No such leasing status: %s.' % field)
    return (True, None)


def valid_class_of_space(field):
    '''Check for a valid enum in a leasing status field.'''
    if field.upper() not in _CLASS_OF_SPACE:
        return (False, 'No such class of space %s.' % field)
    return (True, None)


def valid_integer(field, min_value=None, max_value=None):
    '''Check for integer field.'''
    try:
        int(field)
    except ValueError:
        return (False, 'Not an integer: %s.' % field)
    value = int(field)
    # Perform bounds check.
    if min_value is not None and min_value > value:
        return (False, 'Integer outside of min bounds: %d.' % value)
    if max_value is not None and max_value < value:
        return (False, 'Integer outside of max bounds: %d.' % value)
    return (True, None)


def valid_float(field, min_value=None, max_value=None, precision=None):
    '''Check for float field.'''
    try:
        float(field)
    except ValueError:
        return (False, 'Not a float: %s.' % field)
    value = float(field)
    # Check for precision.
    if precision is not None:
        float_regex = ('^\d+\.\d{%d}$' % precision) if precision else '^\d+$'
        result, _ = _check_regex_field(float_regex, field)
        if not result:
            return (False, 'Precision does not match.')
    # Perform bounds check.
    if min_value is not None and min_value > value:
        return (False, 'Float outside of min bounds: %f.' % value)
    if max_value is not None and max_value < value:
        return (False, 'Float outside of max bounds: %f.' % value)
    return (True, None)
