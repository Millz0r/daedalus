import daedalus.exceptions
import mock
import unittest

from daedalus.frontend.handlers import QueueingRequestHandler, jobify

class MockHandler(QueueingRequestHandler):
    queue_name = 'mock_queue'

    @jobify
    def get(self):
        pass

class BadMockHandler(QueueingRequestHandler):
    pass

class TestQueueingRequestHandler(unittest.TestCase):
    @mock.patch('daedalus.queueing.queue_manager.get_producer')
    @mock.patch('daedalus.queueing.queue_manager.get_queue')
    def test_initialize(self,  get_queue_mock, get_producer_mock):
        application = mock.MagicMock()
        request = mock.MagicMock()
        mock_handler = MockHandler(application, request)
        get_queue_mock.assert_called_with('mock_queue', temp=True)
        get_producer_mock.assert_called_with(on_return=mock_handler.publish_fail)

    @mock.patch('daedalus.queueing.queue_manager.get_producer')
    @mock.patch('daedalus.queueing.queue_manager.get_queue')
    def test_publish(self,  get_queue_mock, get_producer_mock):
        application = mock.MagicMock()
        request = mock.MagicMock()
        mock_handler = MockHandler(application, request)
        mock_request_message = daedalus.queueing.messages.RequestMessage()
        with mock.patch.object(mock_handler.producer, 'publish') as publish_mock:
            with mock.patch.object(mock_request_message, 'yamlize', return_value='I am YAML'):
                mock_handler.publish(mock_request_message)
                publish_mock.assert_called_with('I am YAML', serializer='yaml', routing_key='mock_queue')

    @mock.patch('daedalus.queueing.queue_manager.get_producer')
    @mock.patch('daedalus.queueing.queue_manager.get_queue')
    def test_publish_no_queue(self,  get_queue_mock, get_producer_mock):
        application = mock.MagicMock()
        request = mock.MagicMock()
        mock_handler = BadMockHandler(application, request)
        mock_request_message = daedalus.queueing.messages.RequestMessage()
        with self.assertRaisesRegexp(daedalus.exceptions.MissingQueue, 'Cannot publish to a non-existant queue: None'):
            mock_handler.publish(mock_request_message)

    @mock.patch('daedalus.queueing.queue_manager.get_producer')
    @mock.patch('daedalus.queueing.queue_manager.get_queue')
    def test_publish_no_request_message(self,  get_queue_mock, get_producer_mock):
        application = mock.MagicMock()
        request = mock.MagicMock()
        mock_handler = MockHandler(application, request)
        with self.assertRaisesRegexp(daedalus.exceptions.InvalidRequestMessage, 'Queueing request handlers can only publish request messages.'):
            mock_handler.publish('message')

class TestJobify(unittest.TestCase):
    @mock.patch('uuid.uuid4', return_value='666')
    def test_jobify(self, uuid_mock):
        application = mock.MagicMock()
        request = mock.MagicMock()
        expected_get_calls = [mock.call('x-callback-url', None), mock.call('username')]
        mock_handler = MockHandler(application, request)
        with mock.patch.object(mock_handler, 'set_header') as set_header_mock:
            mock_handler.get()
            uuid_mock.assert_called_with()
            self.assertEqual(mock_handler.job_id, '666')
            set_header_mock.assert_called_with('x-job-id', '666')
            self.assertEqual(request.headers.get.call_args_list, expected_get_calls)

    def test_no_callback_url(self):
        application = mock.MagicMock()
        request = mock.MagicMock()
        mock_handler = MockHandler(application, request)
        with mock.patch.object(mock_handler, 'set_status') as set_status_mock:
            with mock.patch.object(mock_handler, 'write') as write_mock:
                request.headers.get.return_value = None
                mock_handler.get()
                set_status_mock.assert_called_with(400)
                write_mock.assert_called_with({'error': 'no x-callback-url header found'})
