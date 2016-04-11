import daedalus.config
import daedalus.queueing.messages
import json
import kombu
import mock
import requests
import unittest

from daedalus.queueing.mixins import _make_request, ResponderMixin

class ResponseMock(object):
    def __init__(self, status):
        self.status_code = status

class TestResponder(ResponderMixin):
    pass

class MakeRequestTest(unittest.TestCase):
    def setUp(self):
        self.response_message = daedalus.queueing.messages.ResponseMessage()
        self.response_message.callback_url = 'http://localhost'
        self.response_message.body = 'foobar'
        self.response_message.set_header('start_time', 'foo')
        self.response_message.set_header('end_time', 'bar')
        self.response_message.username = 'foo'

    @mock.patch('daedalus.common.auth.get_token', return_value='1234')
    @mock.patch('requests.post', return_value='post_return')
    @mock.patch('daedalus.common.security.Signature', auto_spec=True)
    @mock.patch('multiprocessing.Queue', auto_spec=True)
    def test_no_connection_error(self, queue_mock, signature_mock, request_mock, get_token_mock):
        _make_request(queue_mock, self.response_message)
        request_mock.assert_called_with('http://localhost', headers=self.response_message.get_headers(key_format='html'), data='foobar', auth=signature_mock('1234'), timeout=10)
        queue_mock.put.assert_called_with('post_return')

    @mock.patch('daedalus.common.auth.get_token', return_value='1234')
    @mock.patch('requests.post', side_effect=requests.ConnectionError('BOOM!'))
    @mock.patch('daedalus.common.security.Signature', auto_spec=True)
    @mock.patch('multiprocessing.Queue', auto_spec=True)
    def test_connection_error(self, queue_mock, signature_mock, request_mock, get_token_mock):
        _make_request(queue_mock, self.response_message)
        request_mock.assert_called_with('http://localhost', headers=self.response_message.get_headers(key_format='html'), data='foobar', auth=signature_mock('1234'), timeout=10)
        self.assertFalse(queue_mock.called)


class ResponderMixinTest(unittest.TestCase):
    @mock.patch('multiprocessing.Queue', auto_spec=True)
    @mock.patch('daedalus.queueing.queue_manager.get_response_queue', return_value=mock.MagicMock())
    @mock.patch('daedalus.queueing.queue_manager.get_connection')
    def setUp(self, get_connection_mock, get_response_queue, multiprocessing_queue_mock):
        self.responder = TestResponder()
        get_connection_mock.assert_called_with()
        get_response_queue.assert_called_with()
        multiprocessing_queue_mock.assert_called_with()
        self.assertEqual(self.responder.process_task_function, _make_request)

    @mock.patch('multiprocessing.Process', auto_spec=True, return_value=mock.MagicMock())
    @mock.patch('kombu.message.Message', auto_spec=True)
    def test_handle_message(self, message_mock, process_mock):
        body = '''!ResponseMessage
        _headers:
          job_id: 4
          callback_url: http://localhost
          start_time: foo
          end_time: bar
        body:
          a: 1
        '''
        self.responder.process_queue.get_nowait.return_value = ResponseMock(200)
        with mock.patch('daedalus.queueing.messages.ResponseMessage.load', return_value='response_message_mock'):
            self.responder.handle_message(body, message_mock)
            process_mock.assert_called_with(target=_make_request, args=(self.responder.process_queue, 'response_message_mock'))
            process_mock().start.assert_called_with()
            process_mock().join.assert_called_with()
            message_mock.ack.assert_called_with()

    @mock.patch('multiprocessing.Process', auto_spec=True, return_value=mock.MagicMock())
    @mock.patch('kombu.message.Message', auto_spec=True)
    def test_handle_message_error_status(self, message_mock, process_mock):
        body = '''!ResponseMessage
        _headers:
          job_id: 4
          callback_url: http://localhost
          start_time: foo
          end_time: bar
        body:
          a: 1
        '''
        self.responder.process_queue.get_nowait.return_value = ResponseMock(400)
        with mock.patch('daedalus.queueing.messages.ResponseMessage.load', return_value='response_message_mock'):
            self.responder.handle_message(body, message_mock)
            process_mock.assert_called_with(target=_make_request, args=(self.responder.process_queue, 'response_message_mock'))
            process_mock().start.assert_called_with()
            process_mock().join.assert_called_with()
            message_mock.reject.assert_called_with()

    def test_get_consumers(self):
        self.assertIsInstance(self.responder.get_consumers(mock.MagicMock(), mock.MagicMock()), list)
