'''Helper module for managing our connection to the logging facilities.'''

import daedalus.config
import logging

__FORMAT__ = r'%(asctime)s %(levelname)s: %(message)s'

def _get_log_level():
    '''Parses the LOG_LEVEL config var and makes it into an actionable log level.'''
    return getattr(logging, daedalus.config.LOG_LEVEL, logging.INFO)

def debug(message):
    '''Wrapper for logging debug.'''
    logging.debug(message)

def info(message):
    '''Wrapper for logging info.'''
    logging.info(message)

def warn(message):
    '''Wrapper for logging warn.'''
    logging.warn(message)

def error(message):
    '''Wrapper for logging error.'''
    logging.error(message)

def critical(message):
    '''Wrapper for logging critical.'''
    logging.critical(message)

logging.basicConfig(format=__FORMAT__, level=_get_log_level())
