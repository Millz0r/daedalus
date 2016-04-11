# pylint: disable=invalid-name,no-value-for-parameter
''' Helper methods to handle authentication '''

import base64
import daedalus.config
import daedalus.exceptions

from urlparse import urlparse

from daedalus.common.auth.models import Caller
from daedalus.common.db import DBSession
from daedalus.config import ALLOWED_DOMAINS

def _parse_auth_string(auth_string):
    '''Pulls username and token out of the auth string.'''
    try:
        auth_type, data = auth_string.split(' ', 1)
        assert auth_type == 'Basic'
        return base64.b64decode(data).split(':', 1)
    except (AssertionError, TypeError, AttributeError, ValueError):
        raise daedalus.exceptions.InvalidAuthorizationHeader('Header is invalid: %r' % auth_string)

def _check_caller(username, token, callback_url):
    '''Checks the `username` and `token` match and `callback_url` is allowed.'''
    try:
        assert token == get_token(username)
        if callback_url:
            assert callback_url in ALLOWED_DOMAINS
        return True
    except AssertionError:
        return False
    except daedalus.exceptions.UnknownUsername:
        return False

def check_auth(auth_string, callback_url=None):
    '''Parses auth string and checks to make sure username and token match.'''
    if not auth_string:
        return False

    try:
        username, token = _parse_auth_string(auth_string)
    except daedalus.exceptions.InvalidAuthorizationHeader:
        return False

    if callback_url:
        netloc = urlparse(callback_url).netloc
        if netloc == '':
            return False
        callback_url = netloc

    return _check_caller(username, token, callback_url)

def get_username(auth_string):
    '''Gets the username from the auth_string.'''
    username, _ = _parse_auth_string(auth_string)
    return username

@DBSession()
def get_token(username, _db_session):
    '''Gets the token for a given user from the auth dict.'''
    caller = _db_session.query(Caller).filter_by(username=username).first()
    if caller is None:
        raise daedalus.exceptions.UnknownUsername('No token for username: %r' % username)
    return caller.token
