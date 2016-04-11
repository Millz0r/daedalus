'''Helpers for asserting datatypes.'''
import decimal

def is_decimal(value):
    '''Checks to see if the value is an arbitrary precision decimal number.'''
    return isinstance(value, decimal.Decimal)

def is_list_of_decimals(values):
    '''Checks to see if the values are all arbitrary precision decimal numbers.'''
    return reduce(lambda x, y: x and y, [is_decimal(value) for value in values])
