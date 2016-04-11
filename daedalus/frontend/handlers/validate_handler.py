# pylint: disable=no-member
'''Classes for handling the /validate route.'''

from daedalus.frontend.handlers.queueing_request_handler import QueueingRequestHandler, jobify

class ValidateHandler(QueueingRequestHandler):
    '''Handles the document validation route.'''

    queue_name = 'validation'

    @classmethod
    def route(cls):
        '''Route definition for the application.'''
        return (r'/tape/validate', cls)

    @jobify
    def post(self):
        '''Starts a job to validate a document.'''
        self.request_message.body = self.request.body
        self.publish(self.request_message)
