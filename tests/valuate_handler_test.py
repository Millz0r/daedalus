import mock
import unittest

from daedalus.frontend.handlers import ValuateHandler

class TestValuateHandler(unittest.TestCase):
    def setUp(self):
        application = mock.MagicMock()
        request = mock.MagicMock()
        self.valuate_handler = ValuateHandler(application, request)
        self.valuate_handler.request_message = mock.MagicMock()
        self.valuate_handler.request = mock.MagicMock()
        self.valuate_handler.request.body = 'foobar'

    def test_route(self):
        result = ValuateHandler.route()
        self.assertEqual('/valuate', result[0])
        self.assertEqual(ValuateHandler, result[1])

    @mock.patch('daedalus.xlstransform.transforms.transform', return_value='{"json": "object"}')
    def test_post(self, transform_mock):
        self.valuate_handler.post()
        transform_mock.assert_called_with(self.valuate_handler.request.body, target_format='json')
        self.assertEqual(self.valuate_handler.request_message.body, '{"json": "object"}')

    @mock.patch('daedalus.xlstransform.transforms.transform', side_effect=ValueError('BOOM!'))
    def test_post_bad_transform(self, transform_mock):
        with mock.patch.object(self.valuate_handler, 'write') as write_mock:
            with mock.patch.object(self.valuate_handler, 'set_status') as set_status_mock:
                self.valuate_handler.post()
                transform_mock.assert_called_with(self.valuate_handler.request.body, target_format='json')
                set_status_mock.assert_called_with(400)
                write_mock.assert_called_with({'error': 'BOOM!'}) 
