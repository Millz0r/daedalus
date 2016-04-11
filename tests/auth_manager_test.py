import base64
import mock
import unittest

from daedalus.common import auth
from daedalus.common.auth.models import Caller
from daedalus.common.db import DBSession
from daedalus.exceptions import InvalidAuthorizationHeader, UnknownUsername
from . import MockDatabaseTest

def make_auth_string(username, token):
    return 'Basic %s' % base64.b64encode('%s:%s' % (username, token))

class ParseAuthStringTest(unittest.TestCase):
    def test_parse_auth_string_none(self):
        with self.assertRaisesRegexp(InvalidAuthorizationHeader, 'Header is invalid: None'):
            auth._parse_auth_string(None)

    def test_parse_auth_string_malformed(self):
        with self.assertRaisesRegexp(InvalidAuthorizationHeader, 'alsdfasdfasdf'):
            auth._parse_auth_string('alsdfasdfasdf')

    def test_parse_auth_string_good(self):
        auth_string = make_auth_string('foo', 'bar')
        username, token = auth._parse_auth_string(auth_string)
        self.assertEqual(username, 'foo')
        self.assertEqual(token, 'bar')

class CheckCallerTest(MockDatabaseTest):
    def setUp(self):
        super(CheckCallerTest, self).setUp()
        valid_caller = Caller(username='bar', token='foo')
        DBSession.SESSIONMAKER().query(Caller).filter_by(username='bar').first.return_value = valid_caller
        self.username = 'bar'
        self.password = 'foo'

    def test_good(self):
        with mock.patch('daedalus.common.auth.ALLOWED_DOMAINS', ['baz.com', 'localhost']):
            callback_url = None
            self.assertTrue(auth._check_caller(self.username, self.password, callback_url))
            callback_url = 'localhost'
            self.assertTrue(auth._check_caller(self.username, self.password, callback_url))
            callback_url = 'baz.com'
            self.assertTrue(auth._check_caller(self.username, self.password, callback_url))

    def test_bad_username(self):
        with mock.patch('daedalus.common.auth.ALLOWED_DOMAINS', ['baz.com', 'localhost']):
            self.username = 'quux'
            callback_url = None
            self.assertFalse(auth._check_caller(self.username, self.password, callback_url))
            callback_url = 'localhost'
            self.assertFalse(auth._check_caller(self.username, self.password, callback_url))
            callback_url = 'baz.com'
            self.assertFalse(auth._check_caller(self.username, self.password, callback_url))

    def test_bad_token(self):
        with mock.patch('daedalus.common.auth.ALLOWED_DOMAINS', ['baz.com', 'localhost']):
            self.password = 'quux'
            callback_url = None
            self.assertFalse(auth._check_caller(self.username, self.password, callback_url))
            callback_url = 'localhost'
            self.assertFalse(auth._check_caller(self.username, self.password, callback_url))
            callback_url = 'baz.com'
            self.assertFalse(auth._check_caller(self.username, self.password, callback_url))

    def test_bad_url(self):
        with mock.patch('daedalus.common.auth.ALLOWED_DOMAINS', ['baz.com', 'localhost']):
            callback_url = 'http://example.com'
            self.assertFalse(auth._check_caller(self.username, self.password, callback_url))

    def test_invalid_url(self):
        with mock.patch('daedalus.common.auth.ALLOWED_DOMAINS', ['baz.com', 'localhost']):
            callback_url = 'http://example.com'
            self.assertFalse(auth._check_caller(self.username, self.password, callback_url))

class CheckAuthTest(unittest.TestCase):
    @mock.patch('daedalus.common.auth._check_caller')
    def test_good(self, mock_check_caller):
        auth_string = make_auth_string('bar', 'foo')
        callback_url = 'http://baz.com'
        auth.check_auth(auth_string, callback_url)
        mock_check_caller.assertCalledOnceWith('bar', 'foo', callback_url)

    @mock.patch('daedalus.common.auth._check_caller')
    def test_bad_auth_string(self, mock_check_caller):
        auth_string = "foobar"
        self.assertFalse(auth.check_auth(auth_string))
        self.assertFalse(mock_check_caller.called)
        self.assertFalse(auth.check_auth(None))
        self.assertFalse(mock_check_caller.called)

    @mock.patch('daedalus.common.auth._check_caller')
    def test_invalid_url(self, mock_check_caller):
        auth_string = make_auth_string('bar', 'foo')
        self.assertFalse(auth.check_auth(auth_string, 'example.com'))
        self.assertFalse(mock_check_caller.called)

class GetUsernameTest(unittest.TestCase):
    def test_good(self):
        auth_string = make_auth_string('bar', 'foo')
        self.assertEqual('bar', auth.get_username(auth_string))

    def test_bad(self):
        auth_string = 'asfdadsfasdfbadauthstring'
        with self.assertRaisesRegexp(InvalidAuthorizationHeader, 'Header is invalid: \'asfdadsfasdfbadauthstring\''):
            auth.get_username(auth_string)

class GetTokenTest(MockDatabaseTest):
    def setUp(self):
        super(GetTokenTest, self).setUp()
        valid_caller = Caller(username='bar', token='foo')
        DBSession.SESSIONMAKER().query(Caller).filter_by(username='bar').first.return_value = valid_caller

    def test_good(self):
        self.assertTrue(auth._check_caller("bar", "foo", None))
        self.assertEqual('foo', auth.get_token('bar'))

    def test_bad(self):
        DBSession.SESSIONMAKER().query(Caller).filter_by(username='quux').first.return_value = None
        with self.assertRaisesRegexp(UnknownUsername, 'No token for username: \'quux\''):
            self.assertEqual('foo', auth.get_token('quux'))
