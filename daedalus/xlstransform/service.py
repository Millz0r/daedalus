'''Service for handling xlstransform jobs.'''

import daedalus.common.service
import daedalus.common.mimetype
import daedalus.config
import daedalus.queueing.mixins

class TransformConsumer(daedalus.queueing.mixins.ConsumerMixin):
    '''Answers jobs on the xlstransform queue.'''

    queue_name = 'xlstransform'

    def process_task(self, request, response):
        incoming_file = request.body.get('data')
        source_format = request.body.get('source_format')
        target_format = request.body.get('target_format')

        response.body = daedalus.xlstransform.transform(incoming_file, source_format, target_format)
        response.set_header('content_type', daedalus.common.mimetype.simple_to_mimetype(target_format))

def main():
    '''Starts the daemon that is responsible for listening to rabbitmq.'''
    daedalus.common.service.preflight(__file__)
    consumer = TransformConsumer()
    consumer.run()
