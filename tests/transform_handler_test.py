import mock
import unittest

from daedalus.frontend.handlers import TransformHandler

class TestTransformHandler(unittest.TestCase):
    def setUp(self):
        self.application = mock.MagicMock()
        self.request = mock.MagicMock()
        self.request.headers = {}
        self.transform_handler = TransformHandler(self.application, self.request)

    def test_route(self):
        result = TransformHandler.route()
        self.assertEqual('/transform', result[0])
        self.assertEqual(TransformHandler, result[1])

    def test_post_bad_source_format(self):
        self.request.headers['x-callback-url'] = 'http://localhost'
        self.request.headers['content-type'] = 'bad_format'
        self.request.headers['accept'] = 'application/json'
        with mock.patch.object(self.transform_handler, 'write') as write_mock:
            with mock.patch.object(self.transform_handler, 'set_status') as set_status_mock:
                self.transform_handler.post()
                set_status_mock.assert_called_with(400)
                write_mock.assert_called_with({'error': 'unsupported source format: \'bad_format\''})

    def test_post_bad_target_format(self):
        self.request.headers['x-callback-url'] = 'http://localhost'
        self.request.headers['content-type'] = 'application/json'
        self.request.headers['accept'] = 'bad_format'
        with mock.patch.object(self.transform_handler, 'write') as write_mock:
            with mock.patch.object(self.transform_handler, 'set_status') as set_status_mock:
                self.transform_handler.post()
                set_status_mock.assert_called_with(400)
                write_mock.assert_called_with({'error': 'unsupported target format: \'bad_format\''})

    def test_post_same_args(self):
        self.request.headers['x-callback-url'] = 'http://localhost'
        self.request.headers['content-type'] = 'application/json'
        self.request.headers['accept'] = 'application/json'
        with mock.patch.object(self.transform_handler, 'write') as write_mock:
            with mock.patch.object(self.transform_handler, 'set_status') as set_status_mock:
                self.transform_handler.post()
                set_status_mock.assert_called_with(400)
                write_mock.assert_called_with({'error': 'source format (json) and target format (json) are the same'})

    def test_post_good_args(self):
        # Don't test job_id or callback_url because that's tested in jobify
        self.request.headers['content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        self.request.headers['accept'] = 'application/json'
        self.request.headers['x-callback-url'] = 'http://localhost'
        with mock.patch.object(self.transform_handler, 'publish') as publish_mock:
            with mock.patch('uuid.uuid4', return_value='666'):
                with mock.patch('daedalus.queueing.messages.RequestMessage', auto_spec=True) as request_message_mock:
                    self.transform_handler.request.body = 'foobar'
                    self.transform_handler.post()
                    publish_mock.assert_called_with(request_message_mock())
