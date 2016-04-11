# pylint: disable=no-member
'''Classes for handling the /valuate route.'''

import daedalus.xlstransform.transforms
from daedalus.frontend.handlers.queueing_request_handler import QueueingRequestHandler, jobify

class ValuateHandler(QueueingRequestHandler):
    '''Handles the document transformation route.'''

    queue_name = 'valuate'

    @classmethod
    def route(cls):
        '''Route definition for the application.'''
        return (r'/valuate', cls)

    @jobify
    def post(self):
        '''Valuates a thing.'''
        try:
            incoming_file = daedalus.xlstransform.transforms.transform(self.request.body, target_format='json')
        except Exception as error: # pylint: disable=W0703
            self.set_status(400)
            self.write({'error': error.message})
            return

        self.request_message.body = incoming_file
