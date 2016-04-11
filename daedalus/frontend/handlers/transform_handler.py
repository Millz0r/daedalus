# pylint: disable=no-member
'''Classes for handling the /transform route.'''

import daedalus.common.mimetype
import daedalus.exceptions

from daedalus.frontend.handlers.queueing_request_handler import QueueingRequestHandler, jobify

class TransformHandler(QueueingRequestHandler):
    '''Handles the document transformation route.'''

    queue_name = 'xlstransform'

    @classmethod
    def route(cls):
        '''Route definition for the application.'''
        return (r'/transform', cls)

    @jobify
    def post(self):
        '''Starts a job to transform a document from the Content-Type format to the Accept format.'''
        source_mimetype = self.request.headers.get('content-type')
        try:
            source_format = daedalus.common.mimetype.mimetype_to_simple(source_mimetype)
        except daedalus.exceptions.BadFileFormat:
            self.set_status(400)
            self.write({'error': 'unsupported source format: %r' % source_mimetype})
            return

        target_mimetype = self.request.headers.get('accept')
        try:
            target_format = daedalus.common.mimetype.mimetype_to_simple(target_mimetype)
        except daedalus.exceptions.BadFileFormat:
            self.set_status(400)
            self.write({'error': 'unsupported target format: %r' % target_mimetype})
            return

        if source_format == target_format:
            self.set_status(400)
            self.write({'error': 'source format (%s) and target format (%s) are the same' % (source_format, target_format)})
            return

        incoming_file = self.request.body

        self.request_message.body = {
            'data': incoming_file,
            'target_format': target_format,
            'source_format': source_format
        }

        self.publish(self.request_message)
