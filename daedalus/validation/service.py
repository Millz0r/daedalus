'''Service for handling tape validation jobs.'''

import daedalus.common.service
import daedalus.queueing.mixins
import daedalus.validation

class ValidationConsumer(daedalus.queueing.mixins.ConsumerMixin):
    '''Answers jobs on the validation queue.'''

    queue_name = 'validation'

    def process_task(self, request, response):
        incoming_file = request.body
        response.body = daedalus.validation.validate(incoming_file)

def main():
    '''Starts the daemon that is responsible for listening to rabbitmq.'''
    daedalus.common.service.preflight(__file__)
    consumer = ValidationConsumer()
    consumer.run()
