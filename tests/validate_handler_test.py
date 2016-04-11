import mock
import unittest

from daedalus.frontend.handlers import ValidateHandler

class TestValidateHandler(unittest.TestCase):
    def setUp(self):
        self.application = mock.MagicMock()
        self.request = mock.MagicMock()
        self.request.headers = {}
        self.request.body = 'foobar'
        self.validate_handler = ValidateHandler(self.application, self.request)

    def test_route(self):
        result = ValidateHandler.route()
        self.assertEqual('/tape/validate', result[0])
        self.assertEqual(ValidateHandler, result[1])

    def test_post_no_callback(self):
        with mock.patch.object(self.validate_handler, 'write') as write_mock:
            with mock.patch.object(self.validate_handler, 'set_status') as set_status_mock:
                self.validate_handler.post()
                set_status_mock.assert_called_with(400)
                write_mock.assert_called_with({'error': 'no x-callback-url header found'})

    def test_post(self):
        self.request.headers['content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        self.request.headers['x-callback-url'] = 'http://localhost'
        with mock.patch.object(self.validate_handler, 'publish') as publish_mock:
            with mock.patch('uuid.uuid4', return_value='666'):
                self.validate_handler.post()
                self.assertEqual(publish_mock.call_count, 1)
                self.assertEqual(self.validate_handler.request_message.body, 'foobar')
