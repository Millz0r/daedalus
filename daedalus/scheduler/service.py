'''Service that runs the scheduler.'''

import daedalus.common.service
import daedalus.config
import daedalus.queueing.mixins

class Scheduler(daedalus.queueing.mixins.ResponderMixin):
    '''Implements a default responding behavior.'''

def main():
    '''Starts the demon that is responsible for listening to rabbitmq.'''
    daedalus.common.service.preflight(__file__)
    scheduler = Scheduler()
    scheduler.run()
