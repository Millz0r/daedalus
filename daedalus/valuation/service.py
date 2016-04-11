'''Service for handling valuation jobs.'''

import daedalus.common.service
import daedalus.config
import daedalus.queueing.mixins

class ValuationConsumer(daedalus.queueing.mixins.ConsumerMixin):
    '''Answers jobs on the valuation queue.'''

    queue_name = 'valuation'

    def process_task(self, request, response):
        incoming_file = request.body

        response.set_header('content_type', 'application/json')
        response.body = daedalus.valuation.valuate(incoming_file)

def main():
    '''Starts the demon that is responsible for listening to rabbitmq.'''
    daedalus.common.service.preflight(__file__)
    consumer = ValuationConsumer()
    consumer.run()
