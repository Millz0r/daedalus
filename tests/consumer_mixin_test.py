import daedalus.xlstransform
import json
import kombu
import mock
import unittest

from daedalus.queueing import queue_manager
from daedalus.queueing.mixins import ConsumerMixin

class TestConsumer(ConsumerMixin):
    queue_name = 'foobar'

class ConsumerMixinTest(unittest.TestCase):

    @mock.patch('daedalus.queueing.queue_manager.get_response_queue')
    @mock.patch('daedalus.queueing.queue_manager.get_queue')
    @mock.patch('daedalus.queueing.queue_manager.get_producer', return_value=mock.MagicMock())
    @mock.patch('daedalus.queueing.queue_manager.get_connection')
    def setUp(self, get_connection_mock, get_producer_mock, get_queue_mock, get_response_queue):
        self.consumer = TestConsumer()
        get_connection_mock.assert_called_with()
        get_producer_mock.assert_called_with(on_return=self.consumer.publish_fail)
        get_queue_mock.assert_called_with('foobar')
        get_response_queue.assert_called_with()

    @mock.patch('daedalus.queueing.queue_manager.get_queue', return_value='foobar_queue')
    def test_get_consumers(self, get_queue_mock):
        self.assertIsInstance(self.consumer.get_consumers(mock.MagicMock(), mock.MagicMock()), list)
        get_queue_mock.assert_called_with('foobar')

    def test_process_task(self):
        self.assertEqual(self.consumer.process_task(mock.MagicMock(), mock.MagicMock()), NotImplemented)

    @mock.patch('datetime.datetime', auto_spec=True)
    @mock.patch('kombu.message.Message', auto_spec=True)
    def test_handle_message(self, message_mock, datetime_mock):
        body = '''!RequestMessage
        _headers:
          job_id: 4
          callback_url: http://localhost
        '''
        request_message_mock = daedalus.queueing.messages.RequestMessage.load(body)
        response_message_mock = daedalus.queueing.messages.ResponseMessage()
        with mock.patch.object(self.consumer, 'process_task') as process_task_mock:
            with mock.patch.object(self.consumer.producer, 'publish') as publish_mock:
                with mock.patch('daedalus.queueing.messages.RequestMessage.load', return_value=request_message_mock):
                    with mock.patch('daedalus.queueing.messages.ResponseMessage.from_request_message', return_value=response_message_mock):
                        with mock.patch.object(response_message_mock, 'yamlize', return_value='I am YAML'):
                            process_task_mock.return_value = {'result': 'candy!'}
                            datetime_mock.now.return_value = datetime_mock
                            datetime_mock.ctime.side_effect = ['foo', 'bar']
                            self.consumer.handle_message(body, message_mock)
                            process_task_mock.assert_called_with(request_message_mock, response_message_mock)
                            publish_mock.assert_called_with('I am YAML', serializer='yaml', routing_key='response')
                            message_mock.ack.assert_called_with()

    @mock.patch('kombu.message.Message', auto_spec=True)
    def test_handle_message_error(self, message_mock):
        body = '''!RequestMessage
        _headers:
          job_id: 4
          callback_url: http://localhost
        '''
        request_message_mock = daedalus.queueing.messages.RequestMessage.load(body)
        response_message_mock = daedalus.queueing.messages.ResponseMessage()
        with mock.patch.object(self.consumer, 'process_task') as process_task_mock:
            with mock.patch.object(self.consumer.producer, 'publish') as publish_mock:
                with mock.patch('daedalus.queueing.messages.RequestMessage.load', return_value=request_message_mock):
                    with mock.patch('daedalus.queueing.messages.ResponseMessage.from_request_message', return_value=response_message_mock):
                        with mock.patch.object(response_message_mock, 'yamlize', return_value='I am YAML'):
                            process_task_mock.side_effect = ValueError('BOOM!')
                            self.consumer.handle_message(body, message_mock)
                            process_task_mock.assert_called_with(request_message_mock, response_message_mock)
                            self.assertEqual(json.loads(response_message_mock.error), {'error': 'BOOM!'})
                            publish_mock.assert_called_with('I am YAML', serializer='yaml', routing_key='response')
                            message_mock.reject.assert_called_with()
