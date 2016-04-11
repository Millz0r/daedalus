import base64
import mock
import sys
import unittest

from cyclone.httpserver import HTTPRequest

from daedalus.common.auth.models import Caller
from daedalus.common.db import DBSession
from daedalus.frontend.secure_application import SecureApplication, JsonErrorHandler
from . import MockDatabaseTest

class JsonErrorHandlerTest(unittest.TestCase):
    def setUp(self):
        self.error_handler = JsonErrorHandler(mock.MagicMock(), mock.MagicMock(), status_code=401)

    def test_error_message_401(self):
        self.assertEqual(JsonErrorHandler.get_error_message(401), 'Unauthorized')

    def test_error_message_bad_key(self):
        self.assertEqual(JsonErrorHandler.get_error_message(9001), 'Unknown error')

    def test_write_error(self):
        with mock.patch.object(self.error_handler, 'write') as write_mock:
            self.error_handler.write_error(401)
            write_mock.assert_called_with({'error': 'Unauthorized'})

class SecureApplicationTest(MockDatabaseTest):
    def setUp(self):
        self.secure_application = SecureApplication([])
        self.request = HTTPRequest('GET', 'http://localhost/foobar.txt')
        super(SecureApplicationTest, self).setUp()
        valid_caller = Caller(username='yambo', token='groot?')
        DBSession.SESSIONMAKER().query(Caller).filter_by(username='yambo').first.return_value = valid_caller

    @mock.patch('daedalus.frontend.secure_application.JsonErrorHandler')
    def test_no_authorization(self, error_handler_mock):
        self.secure_application.__call__(self.request)
        error_handler_mock.assert_called_with(self.secure_application, self.request, status_code=401)

    @mock.patch('daedalus.frontend.secure_application.JsonErrorHandler')
    def test_bad_token(self, error_handler_mock):
        self.request.headers.add('Authorization', 'Basic ' + base64.b64encode('yambo:badpass'))
        self.secure_application.__call__(self.request)
        error_handler_mock.assert_called_with(self.secure_application, self.request, status_code=401)

    @mock.patch('daedalus.frontend.secure_application.JsonErrorHandler')
    def test_bad_username(self, error_handler_mock):
        self.request.headers.add('Authorization', 'Basic ' + base64.b64encode('yaniv:groot?'))
        self.secure_application.__call__(self.request)
        error_handler_mock.assert_called_with(self.secure_application, self.request, status_code=401)

    @mock.patch('daedalus.frontend.secure_application.JsonErrorHandler')
    def test_bad_token_case(self, error_handler_mock):
        self.request.headers.add('Authorization', 'Basic ' + base64.b64encode('yaniv:GROOT?'))
        self.secure_application.__call__(self.request)
        error_handler_mock.assert_called_with(self.secure_application, self.request, status_code=401)

    @mock.patch('daedalus.frontend.secure_application.JsonErrorHandler')
    def test_bad_username_case(self, error_handler_mock):
        self.request.headers.add('Authorization', 'Basic ' + base64.b64encode('Yambo:groot?'))
        self.secure_application.__call__(self.request)
        error_handler_mock.assert_called_with(self.secure_application, self.request, status_code=401)

    @mock.patch('cyclone.web.Application')
    def test_good_authorization(self, application_mock):
        self.request.headers.add('Authorization', 'Basic ' + base64.b64encode('yambo:groot?'))
        self.secure_application.__call__(self.request)
        self.assertTrue(application_mock.called)
