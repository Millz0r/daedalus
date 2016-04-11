'''Class for handling requests that queue items.'''

import cyclone.web
import daedalus.queueing.messages
import daedalus.queueing.queue_manager
import functools
import uuid

from daedalus.common import log_manager

class QueueingRequestHandler(cyclone.web.RequestHandler):
    '''Helper class to make generating job id's easy.'''
    queue_name = None

    def initialize(self):
        '''Setup the connection to the work queues.'''
        if self.queue_name:
            self.queue = daedalus.queueing.queue_manager.get_queue(self.queue_name, temp=True) # pylint: disable=W0201
            self.producer = daedalus.queueing.queue_manager.get_producer(on_return=self.publish_fail) # pylint: disable=W0201

    def publish_fail(self, exception, exchange, routing_key, message): # pylint: disable=unused-argument,no-self-use
        '''Callback for when a publish fails.'''
        log_manager.error('Error publishing: %s' % exception.message)

    def publish(self, message):
        '''Helper function to make publishing messages easier.'''
        try:
            assert isinstance(message, daedalus.queueing.messages.RequestMessage)
        except AssertionError:
            log_manager.error('Expected RequestMessage, got %r. Cannot publish.' % message)
            raise daedalus.exceptions.InvalidRequestMessage('Queueing request handlers can only publish request messages.')

        if self.queue_name:
            self.producer.publish(message.yamlize(), serializer='yaml', routing_key=self.queue_name)
        else:
            log_manager.error('Tried to publish to non-existant queue: %s' % self.queue_name)
            raise daedalus.exceptions.MissingQueue('Cannot publish to a non-existant queue: %s' % self.queue_name)

def jobify(method):
    '''Decorator that adds a job id to the request handler, and adds an x-header for the job id.'''
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        '''Decorator function, does the real work.'''
        self.request_message = daedalus.queueing.messages.RequestMessage()
        self.callback_url = self.request.headers.get('x-callback-url', None)
        if not self.callback_url:
            self.set_status(400)
            self.write({'error': 'no x-callback-url header found'})
            return

        self.job_id = str(uuid.uuid4())
        self.set_header('x-job-id', self.job_id)

        self.request_message.job_id = self.job_id
        self.request_message.callback_url = self.callback_url
        # SecureApplication makes sure we *definitely* have a username already
        self.request_message.username = self.request.headers.get('username')

        return method(self, *args, **kwargs)
    return wrapper
