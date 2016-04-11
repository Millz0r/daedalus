#pylint: disable=no-member,maybe-no-member,no-value-for-parameter
'''Responder - responds to items on the response queue.'''

import datetime
import daedalus.common.security
import daedalus.exceptions
import daedalus.queueing.messages
import daedalus.queueing.queue_manager
import kombu
import kombu.mixins
import multiprocessing
import Queue
import requests

from daedalus.common import auth, log_manager

def _make_request(queue, response_message):
    '''Default response processing function. Kicks a webhook url.'''
    url = response_message.callback_url
    data = response_message.get_body_or_error()
    headers = response_message.get_headers(key_format='html')
    token = auth.get_token(response_message.username)
    try:
        queue.put(requests.post(url, timeout=10, data=data, headers=headers, auth=daedalus.common.security.Signature(token)))
    except requests.RequestException as error:
        queue.put(error)

class ConsumerMixin(kombu.mixins.ConsumerMixin):
    '''A class to facilitate pulling items off of work queues, and handing the job off to the responsible library.'''

    def __init__(self):
        '''Requires a string reference to the application module that is to be called when processing new jobs.'''
        self.connection = daedalus.queueing.queue_manager.get_connection()
        self.producer = daedalus.queueing.queue_manager.get_producer(on_return=self.publish_fail)
        self.queue = daedalus.queueing.queue_manager.get_queue(self.queue_name)
        self.response_queue = daedalus.queueing.queue_manager.get_response_queue()

    def publish_fail(self, exception, exchange, routing_key, message): # pylint: disable=unused-argument,no-self-use
        '''Callback for when a publish fails.'''
        log_manager.error('Error publishing: %s' % exception.message)

    def get_consumers(self, KombuConsumer, channel):
        '''Required by the ConsumerMixin.'''
        return [KombuConsumer(daedalus.queueing.queue_manager.get_queue(self.queue_name), accept=['yaml'], callbacks=[self.handle_message])]

    def process_task(self, request_message, response_message): # pylint: disable=W0613,R0201
        '''Overwrite this to actually do the work that needs to be done.'''
        return NotImplemented

    def handle_message(self, request_yaml, message):
        '''Pops a message off the queue and passes the meat to process_task for completion.'''
        request_message = daedalus.queueing.messages.RequestMessage.load(request_yaml)
        response_message = daedalus.queueing.messages.ResponseMessage.from_request_message(request_message)

        try:
            start_time = datetime.datetime.now().ctime()
            log_manager.info('Starting processing task at %s' % start_time)
            self.process_task(request_message, response_message)
            response_message.set_header('start_time', start_time)
            response_message.set_header('end_time', datetime.datetime.now().ctime())
            response_message.set_header('job_status', 'success')
            log_manager.info('Finished processing task at %s' % response_message.get_header('end_time'))
            self.producer.publish(response_message.yamlize(), serializer='yaml', routing_key='response')
            message.ack()
        except Exception as error: # pylint: disable=W0703
            response_message.error = {'error': error.message}
            response_message.set_header('job_status', 'error')
            log_manager.warn('Task failed with error: %s' % error.message)
            self.producer.publish(response_message.yamlize(), serializer='yaml', routing_key='response')
            message.reject()

class ResponderMixin(kombu.mixins.ConsumerMixin):
    '''A class to facilitate pulling items off of response queue, and POSTing it to the callback URL.'''

    def __init__(self, process_task_function=None):
        '''Requires a string reference to the application module that is to be called when processing new jobs.'''
        self.connection = daedalus.queueing.queue_manager.get_connection()
        self.queue = daedalus.queueing.queue_manager.get_response_queue()
        self.process_queue = multiprocessing.Queue()
        self.process_task_function = process_task_function if process_task_function else _make_request

    def get_consumers(self, KombuConsumer, channel):
        '''Required by the ConsumerMixin.'''
        return [KombuConsumer(self.queue, accept=['yaml'], callbacks=[self.handle_message])]

    def handle_message(self, response_yaml, message):
        '''Pops a message off the queue and passes the meat to process_task for completion.'''
        response_message = daedalus.queueing.messages.ResponseMessage.load(response_yaml)

        log_manager.info('Processing callback')
        subprocess = multiprocessing.Process(target=self.process_task_function, args=(self.process_queue, response_message))
        subprocess.start()
        subprocess.join()

        try:
            server_response = self.process_queue.get_nowait()

            # Some ConnectionErrors actually have a response, many don't.
            # If the ConnectionError does have a response, we want to use that response object to figure out what happend
            # Otherwise we just reraise the error. This allows us to do fancy things on 50Xs or 40Xs.
            if isinstance(server_response, Exception):
                if getattr(server_response, 'response', None) is not None:
                    server_response = server_response.response
                else:
                    raise server_response

            if server_response.status_code != 200:
                log_manager.warn('Callback returned with status %d' % server_response.status_code)
                raise daedalus.exceptions.NotOk('bad status (%d)' % server_response.status_code)
            message.ack()
        except (daedalus.exceptions.DaedalusError, requests.RequestException, Queue.Empty) as error: # pylint: disable=W0702
            log_manager.warn(error.message)
            message.reject()
